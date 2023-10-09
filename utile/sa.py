import subprocess
import time

from utile.data import *


def checking_states(sa_job_id):
    """
    this function execute a powershell and run some commands on it
    :return: the results of the commands
    """
    connexion = create_connection("cli_panoptes/data/cli_panoptes.sqlite")
    command = db_select_one(connexion, 'sa_jobs', ('command_script', f'sa_job_id={sa_job_id}'))
    cmd = command[0].split(" ")
    state = subprocess.run(cmd, capture_output=True)
    state_value = state.stdout.decode('utf-8')
    return state_value.strip()


def compare_states(sa_job_id):
    """
    this function compare the two states
    :return: alert message if there is a difference between the default and the obtained state
    """
    con = create_connection("cli_panoptes/data/cli_panoptes.sqlite")
    default_state = db_select_one(con, "sa_jobs",
                                  ('expected_result', f'sa_job_id = {sa_job_id}'))
    obtained_state = checking_states(sa_job_id)
    if default_state[0] != obtained_state:
        timestamp = int(time.time())
        data_sa = (timestamp, 1, sa_job_id)
        db_insert(con, 'sa_events', '(datetime_event,except_active,sa_job_id)', data_sa)
        close_connection(con)
    else:
        return close_connection(con)


def time_to_wait(sa_job_id):
    """
    this function count the time to execute the function after it
    :return:close the connection with the database
    """
    db_connect = create_connection("cli_panoptes/data/cli_panoptes.sqlite")
    time_exe = db_select_one(db_connect, 'sa_jobs',
                             ('schedule', f'sa_job_id = {sa_job_id}'))
    time.sleep(time_exe[0])
    return close_connection(db_connect)
