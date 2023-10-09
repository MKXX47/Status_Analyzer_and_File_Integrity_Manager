import os
import time
from hashlib import *
from glob import iglob
from utile.data import *


def get_files(fim_rule_id):
    """
    this function display's all the files and directories on a folder based on a pattern
    :param fim_rule_id: the fim_rule we are currently working on
    :return: paths to the matching files in the folder
    """
    connection = create_connection("cli_panoptes/data/cli_panoptes.sqlite")
    pattern = db_select_one(connection, 'fim_rules', ('path', f'fim_rule_id={fim_rule_id}'))
    paths_list = []
    for filename in iglob(pattern[0], recursive=True):
        paths_list.append(filename)
    return paths_list


def fingerprint_md5(file_path):
    """
    this function read a file and make he's hash (fingerprint)
    :param file_path: the path to access the file
    :return: the MD5 of the file that was given
    """
    hash_method = md5()
    with open(file_path, 'rb') as input_file:
        buf = input_file.read()
        while len(buf) > 0:
            hash_method.update(buf)
            buf = input_file.read()
    return hash_method.hexdigest()


def fingerprint_sha1(file_path):
    """
    this function read a file and make he's hash (fingerprint)
    :param file_path: the path to access the file
    :return: the SHA1 of the file that was given
    """
    hash_method = sha1()
    with open(file_path, 'rb') as input_file:
        buf = input_file.read()
        while len(buf) > 0:
            hash_method.update(buf)
            buf = input_file.read()
    return hash_method.hexdigest()


def file_details(file_path):
    """
    this function gives details about a file
    :param file_path: the path to access the file details.st_size
    :return: a dictionary of details
    """
    parent_dir = os.path.dirname(file_path)  # os.path.abspath()
    parent_id = os.stat(parent_dir).st_ino
    file_name, file_extension = os.path.splitext(file_path)
    name_extension = [file_name, file_extension]
    name = name_extension[0].split('/')
    hash_md5 = fingerprint_md5(file_path)
    hash_sha1 = fingerprint_sha1(file_path)
    details = os.stat(file_path)
    details_dic = {"file_mode": details.st_mode, "file_inode": details.st_ino, "file_dev": details.st_dev,
                   "file_nlink": details.st_nlink, "file_gid": details.st_gid, "file_uid": details.st_uid,
                   "file_atime": int(details.st_atime), "file_mtime": int(details.st_mtime),
                   "file_ctime": int(details.st_ctime),
                   "file_name": name[-1], "file_type": name_extension[1], "file_md5": hash_md5,
                   "file_sha1": hash_sha1, "parent_id": parent_id, "file_size": details.st_size}

    return details_dic


def insert_ref_images(fim_rule_id):
    """
    this function insert's details into the table ref_images table
    :param fim_rule_id: the fim_rule we are currently working on
    :return: close the connection with the database
    """
    file_paths = get_files(fim_rule_id)  # liste de chemins d'acces au fichiers dans le dossier qu'on va monitorer
    db_con = create_connection("cli_panoptes/data/cli_panoptes.sqlite")
    for path in file_paths:
        timestamp = int(time.time())
        details_dic = file_details(path)
        data = (details_dic["file_inode"], timestamp, details_dic["parent_id"],
                details_dic["file_name"],
                details_dic["file_type"], details_dic["file_mode"], details_dic["file_nlink"], details_dic["file_uid"],
                details_dic["file_gid"], details_dic["file_size"], details_dic["file_atime"], details_dic["file_mtime"],
                details_dic["file_ctime"], details_dic["file_md5"], details_dic["file_sha1"])
        db_insert(db_con, 'ref_images',
                  '(file_inode,datetime_image,parent_id,file_name,file_type,file_mode,file_nlink,file_uid,file_gid,file_size,file_atime,file_mtime,file_ctime,file_md5,file_sha1)',
                  data)
        image_id = db_select_one(db_con, 'ref_images', ('image_id', f'file_inode={details_dic["file_inode"]}'))
        fim_image = (fim_rule_id, image_id[0], details_dic["file_inode"])
        db_insert(db_con, 'fim_image', '(fim_rule_id,image_id,file_inode)', fim_image)
    return close_connection(db_con)


def time_sleep(fim_rule_id):
    """
    this function count the time to execute the functions after it
    :param fim_rule_id: the fim_rule we are currently working on
    :return:close the connection with the database
    """
    db_connect = create_connection("cli_panoptes/data/cli_panoptes.sqlite")
    time_exe = db_select_one(db_connect, 'fim_rules', ('schedule', f'fim_rule_id={fim_rule_id}'))
    time.sleep(time_exe[0])
    return close_connection(db_connect)


def insert_stat_files(fim_rule_id):
    """
    this function insert's details into the table stat_files
    :param fim_rule_id: the fim_rule we are currently working on
    :return: close the connection with the database
    """
    files_paths = get_files(fim_rule_id)  # liste de chemins d'acces au fichiers dans le dossier qu'on va monitorer
    db_conn = create_connection("cli_panoptes/data/cli_panoptes.sqlite")
    inodes = db_select_all(db_conn, 'fim_image', ('file_inode', f'fim_rule_id={fim_rule_id}'))
    files_delete = ()
    for inode in inodes:
        files_delete += inode
    db_delete(db_conn, 'stat_files', f'file_inode in {files_delete}')
    for path in files_paths:
        details_dict = file_details(path)
        data = (details_dict["file_inode"], details_dict["parent_id"],
                details_dict["file_name"],
                details_dict["file_type"], details_dict["file_mode"], details_dict["file_nlink"],
                details_dict["file_uid"],
                details_dict["file_gid"], details_dict["file_size"], details_dict["file_atime"],
                details_dict["file_mtime"],
                details_dict["file_ctime"], details_dict["file_md5"], details_dict["file_sha1"])
        db_insert(db_conn, 'stat_files',
                  '(file_inode,parent_id,file_name,file_type,file_mode,file_nlink,file_uid,file_gid,file_size,file_atime,file_mtime,file_ctime,file_md5,file_sha1)',
                  data)
    return close_connection(db_conn)


def compare_details(fim_rule_id):
    """
    this function compare the old reference image (ref_images) and the new one (stat_files)
    :param fim_rule_id: the fim_rule we are currently working on
    :return: close the connection with the database
    """
    db_connection = create_connection("cli_panoptes/data/cli_panoptes.sqlite")
    images_id = db_select_all(db_connection, 'fim_image', ('image_id', f'fim_rule_id={fim_rule_id}'))

    fim_rules = db_select_one(db_connection, 'fim_rules',
                              ('inode,parent,name,type,mode,nlink,uid,gid,size,atime,mtime,md5,sha1',
                               f'fim_rule_id={fim_rule_id}'))

    checking_dict = {'file_inode': fim_rules[0:1], 'parent_id': fim_rules[1:2], 'file_name': fim_rules[2:3],
                     'file_type': fim_rules[3:4], 'file_mode': fim_rules[4:5], 'file_nlink': fim_rules[5:6],
                     'file_uid': fim_rules[6:7], 'file_gid': fim_rules[7:8], 'file_size': fim_rules[8:9],
                     'file_atime': fim_rules[9:10], 'file_mtime': fim_rules[10:11],
                     'file_md5': fim_rules[11:12],
                     'file_sha1': fim_rules[12:]}
    for i in images_id:
        for key, value in checking_dict.items():
            if value[0] == 1:
                ref_select = db_select_one(db_connection, 'ref_images', (key, f'image_id = {i[0]}'))
                file_inode = db_select_one(db_connection, 'ref_images',
                                           ('file_inode', f'image_id = {i[0]}'))
                stat_select = db_select_one(db_connection, 'stat_files',
                                            (key, f'file_inode = {file_inode[0]}'))
                if ref_select[0] != stat_select[0]:
                    timestamp = int(time.time())
                    data = (timestamp, f'the file {key} has been changed', 1, file_inode[0], i[0], fim_rule_id)
                    db_insert(db_connection, 'fim_events',
                              '(datetime_event,except_msg,except_active,file_inode,image_id,fim_rule_id)', data)
                else:
                    continue
            else:
                continue
    return close_connection(db_connection)
