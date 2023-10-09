import socket
import json
from hashlib import md5
from utile.data import *


def md5_hash(string):
    hash_method = md5()
    string_bytes = str(string).encode('utf-8')
    hash_method.update(string_bytes)
    string_hashed = hash_method.hexdigest()
    return string_hashed


def send_msg(s, msg: str):
    size_msg = len(msg)
    s.send(size_msg.to_bytes(4, byteorder="big"))
    s.send(msg.encode())


def recv_msg(sock):
    len_msg_bytes = sock.recv(4)
    size_msg = int.from_bytes(len_msg_bytes, byteorder='big')
    msg = sock.recv(size_msg).decode()
    return msg


def send_msg_dict(sock, dict_msg):
    msg_byte = json.dumps(dict_msg).encode('utf-8')
    size_msg = len(msg_byte)
    sock.send(size_msg.to_bytes(4, byteorder="big"))
    sock.send(msg_byte)
    sock.send(md5_hash(dict_msg).encode())


def recv_msg_dict(sock):
    len_msg_bytes = sock.recv(4)
    size_msg = int.from_bytes(len_msg_bytes, byteorder='big')
    msg = sock.recv(size_msg)
    dict_msg = json.loads(msg.decode('utf-8'))
    dict_hashed = sock.recv(32).decode()
    if md5_hash(dict_msg) != dict_hashed:
        print('Data has been changed !')
    else:
        pass
    return dict_msg


def event_config():
    event_dict = {'ACTION': 'EVENT', 'FIM_EVENT': [], 'SA_EVENT': []}
    db_con = create_connection('cli_panoptes/data/cli_panoptes.sqlite')
    fim_events = db_select_all(db_con, 'fim_events', ('fim_event_id', '*'))
    sa_events = db_select_all(db_con, 'sa_events', ('sa_event_id', '*'))
    for i in fim_events:
        fim_event = db_select_one(db_con, 'fim_events', ('*', f'fim_event_id={i[0]}'))
        event_dict['FIM_EVENT'].append(list(fim_event))
    for i in sa_events:
        sa_event = db_select_one(db_con, 'sa_events', ('*', f'sa_event_id={i[0]}'))
        event_dict['SA_EVENT'].append(list(sa_event))
    close_connection(db_con)
    return event_dict


def insert_config(dict_config):
    dbcon = create_connection('cli_panoptes/data/cli_panoptes.sqlite')
    jobs = dict_config['SA_JOBS']
    rules = dict_config['FIM_RULES']
    db_delete(dbcon, 'sa_jobs', '*')
    db_delete(dbcon, 'fim_rules', '*')
    for i in jobs:
        db_insert(dbcon, 'sa_jobs',
                  '(sa_job_id,sa_job_name,script,command_script,expected_result,alert_message,schedule)', tuple(i))
    for e in rules:
        db_insert(dbcon, 'fim_rules',
                  '(fim_rule_id,fim_rule_name,path,start_inode,inode,parent,name,type,mode,nlink,uid,gid,size,atime,mtime,md5,sha1,schedule)',
                  tuple(e))
    return close_connection(dbcon)


def connect_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((socket.gethostname(), 8880))
    return sock


message = {'ACTION': 'GET_CONFIG', 'CLI_NAME': 'kali'}
srv_socket = connect_server()
msg_rcv = recv_msg(srv_socket)
print(msg_rcv)
send_msg_dict(srv_socket, message)
data_rcv = recv_msg_dict(srv_socket)
insert_config(data_rcv)
