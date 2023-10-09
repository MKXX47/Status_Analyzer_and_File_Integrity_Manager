import socket
import threading
from hashlib import md5
from utile.data import *
import json


def md5_hash(string):
    """
    this function take's a data and returns the hash
    :param string: the data we want hashed
    :return: the data's fingerprint
    """
    hash_method = md5()
    string_bytes = str(string).encode('utf-8')
    hash_method.update(string_bytes)
    string_hashed = hash_method.hexdigest()
    return string_hashed


def send_msg(s, msg: str):
    """
    this function is used to send simple messages
    :param s: the socket of the receiver
    :param msg: the message we want to send
    """
    size_msg = len(msg)
    s.send(size_msg.to_bytes(4, byteorder="big"))
    s.send(msg.encode())
    s.send(md5_hash(msg).encode())


def recv_msg(s):
    """
    this function receive the simple message and check the integrity of it
    :param s: the sender socket
    :return: the message
    """
    len_msg_bytes = s.recv(4)
    size_msg = int.from_bytes(len_msg_bytes, byteorder='big')
    msg = s.recv(size_msg).decode()
    msg_hashed = s.recv(32).decode()
    if md5_hash(msg) != msg_hashed:
        print('Data have been changed !')
    else:
        pass
    return msg


def send_msg_dict(sock, msg):
    """
    this function is used to send a dictionary
    :param sock: the receiver socket
    :param msg: a dictionary
    """
    msg_byte = json.dumps(msg).encode('utf-8')
    size_msg = len(msg_byte)
    sock.send(size_msg.to_bytes(4, byteorder="big"))
    sock.send(msg_byte)
    sock.send(md5_hash(msg).encode())


def recv_msg_dict(sock):
    """
    this function receive a dictionary and check the integrity of it
    :param sock: the sender socket
    :return: the dictionary
    """
    len_msg_bytes = sock.recv(4)
    size_msg = int.from_bytes(len_msg_bytes, byteorder='big')
    msg = sock.recv(size_msg)

    dict_msg = json.loads(msg.decode('utf-8'))
    dict_hashed = sock.recv(32).decode()
    if md5_hash(dict_msg) != dict_hashed:
        print('Data have been changed !')
    else:
        pass
    return dict_msg


def data_to_send(host_name):
    """
    this function get the hostname  and returns the host configuration
    :param host_name: the name of the client that want the configuration
    :return: the configuration Dictionary
    """
    config_dict = {'ACTION': 'SET_CONFIG ', 'SA_JOBS': [], 'FIM_RULES': []}
    db_conn = create_connection('../srv_panoptes/data/srv_panoptes.sqlite')
    client_id = db_select_one(db_conn, "client", ("client_id", f'hostname = \'{host_name}\''))
    client_sa = db_select_all(db_conn, "client_sa", ("sa_job_id", f'client_id= {client_id[0]}'))
    client_fim = db_select_all(db_conn, "client_fim", ("fim_rule_id", f'client_id= {client_id[0]}'))
    for i in client_sa:
        sa_jobs = db_select_one(db_conn, "sa_jobs", ("*", f'sa_job_id = {i[0]}'))
        config_dict['SA_JOBS'].append(list(sa_jobs))
    for x in client_fim:
        fim_rules = db_select_one(db_conn, "fim_rules", ("*", f'fim_rule_id = {x[0]}'))
        config_dict['FIM_RULES'].append(list(fim_rules))
    close_connection(db_conn)
    return config_dict


def connect_server():
    """
    this function create a connection with the server
    :return: the server socket
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((socket.gethostname(), 8880))
    return sock


def client_thread(client_socket: socket.socket):
    send_msg(client_socket, 'SRV-OK')
    msg_rcv = recv_msg_dict(client_socket)
    while len(msg_rcv) < 0:
        msg_rcv = recv_msg_dict(client_socket)
    if msg_rcv['ACTION'] == 'GET_CONFIG':
        hostname = msg_rcv['CLI_NAME']
        db_con = create_connection('../srv_panoptes/data/srv_panoptes.sqlite')
        host_db = db_select_one(db_con, 'client', ('hostname', f'hostname = \'{hostname}\''))
        if not host_db:
            error = "Client does not exists !"
            send_msg(client_socket, error)
        else:
            config = data_to_send(hostname)
            send_msg_dict(client_socket, config)
    elif msg_rcv['ACTION'] == 'EVENT':
        fim_events = msg_rcv['FIM_EVENT']
        sa_events = msg_rcv['SA_EVENT']
        db_con = create_connection('../srv_panoptes/data/srv_panoptes.sqlite')
        db_delete(db_con, 'sa_events', '*')
        db_delete(db_con, 'fim_events', '*')
        for x in fim_events:
            db_insert(db_con, 'fim_events',
                      '(fim_event_id,datetime_event,except_msg,except_active,file_inode,image_id,fim_rule_id)',
                      tuple(x))
        for y in sa_events:
            db_insert(db_con, 'sa_events', '(sa_event_id,datetime_event,except_active,sa_job_id)', tuple(y))
        send_msg(client_socket, 'EVENT-OK')
    return client_socket.close()


def launch_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((socket.gethostname(), 8880))

    server_socket.listen(5)

    while True:
        client_socket, address = server_socket.accept()
        print(f"[+] received connection from {address}\n")
        ct = threading.Thread(target=client_thread, args=(client_socket,))
        ct.run()


if __name__ == '__main__':
    launch_server()
