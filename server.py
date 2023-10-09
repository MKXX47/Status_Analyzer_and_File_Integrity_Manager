from utile.network import *
from utile.fim import *
from utile.sa import *
from utile.data import *


def thread_fim(fim_rule_id):
    """
    this function is for creating FIM threads
    :param fim_rule_id: the fim_rule that we are working on
    :return: FIM thread
    """
    insert_ref_images(fim_rule_id)
    while True:
        time_sleep(fim_rule_id)
        insert_stat_files(fim_rule_id)
        compare_details(fim_rule_id)


def thread_sa(sa_job_id):
    """
    this function is for creating SA threads
    :param sa_job_id: the sa_job that we are working on
    :return: SA thread
    """
    compare_states(sa_job_id)
    while True:
        time_to_wait(sa_job_id)
        compare_states(sa_job_id)


def event_config():
    """
    this function groups the events in a dictionary
    :return: dictionary of events
    """
    event_dict = {'ACTION': 'EVENT', 'FIM_EVENT': [], 'SA_EVENT': []}
    db_con = create_connection('cli_panoptes/data/cli_panoptes.sqlite')
    fim_events = db_select_all(db_con, 'fim_events', ('fim_event_id', '*'))
    sa_events = db_select_all(db_con, 'sa_events', ('sa_event_id', '*'))
    for a in fim_events:
        fim_event = db_select_one(db_con, 'fim_events', ('*', f'fim_event_id={a[0]}'))
        event_dict['FIM_EVENT'].append(list(fim_event))
    for b in sa_events:
        sa_event = db_select_one(db_con, 'sa_events', ('*', f'sa_event_id={b[0]}'))
        event_dict['SA_EVENT'].append(list(sa_event))
    close_connection(db_con)
    return event_dict


def insert_config(dict_config):
    """
    this function receive a configuration dictionary and insert it in the database
    :param dict_config: configuration dictionary containing fim_rules and sa_jobs
    :return: close the connection with the database
    """
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


#
#
# cette partie c'est pour avoir la configuration et remplir la BD
try:
    message = {'ACTION': 'GET_CONFIG', 'CLI_NAME': 'kali'}  # le hostname de la machine
    srv_socket = connect_server()
    msg_rcv = recv_msg(srv_socket)
    print(msg_rcv)
    send_msg_dict(srv_socket, message)
    data_rcv = recv_msg_dict(srv_socket)
    insert_config(data_rcv)
except ConnectionError:
    print("the server is offline")

#
#
# cette partie pour cree les threads FIM
conn = create_connection('cli_panoptes/data/cli_panoptes.sqlite')
fim_rules = db_select_all(conn, 'fim_rules', ('fim_rule_id', '*'))
for f in fim_rules:
    thread_f = threading.Thread(target=thread_fim, args=(f[0],))
    thread_f.start()
#
#
# cette partie pour cree les threads SA
sa_jobs = db_select_all(conn, 'sa_jobs', ('sa_job_id', '*'))
for s in sa_jobs:
    thread_s = threading.Thread(target=thread_sa, args=(s[0],))
    thread_s.start()
print(threading.active_count())
#
#
# cette partie pour envoyer les events au serveur
while True:
    time.sleep(10)
    try:
        message = event_config()
        srv_socket = connect_server()
        msg_rcv = recv_msg(srv_socket)
        print(msg_rcv)
        send_msg_dict(srv_socket, message)
        data_rcv = recv_msg(srv_socket)
        print(data_rcv)
    except ConnectionError:
        print("the server is offline")
