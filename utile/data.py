import sqlite3


def create_connection(db_file):
    """
    create a connection to the SQLite database
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as error:
        print(error)
    return conn


def db_select_all(db_con, table_name, query):
    """
    this function select rows from a tuple
    :param db_con:database connection
    :param table_name: the name of the table we want to select from
    :param query: the columns and condition
    :return: the match from the table
    """
    cur = db_con.cursor()
    # query = ('column1,colum2,column3', 'column = 1')
    if query[1] == '*':
        sql = f'SELECT {query[0]} FROM {table_name}'
    else:
        sql = f'SELECT {query[0]} FROM {table_name} WHERE {query[1]}'
    cur.execute(sql)
    res = cur.fetchall()
    return res


def db_select_one(db_con, table_name, query):
    """
    this function select rows from a tuple
    :param db_con:database connection
    :param table_name: the name of the table we want to select from
    :param query: the columns and condition
    :return: the match from the table
    """
    cur = db_con.cursor()
    # query = ('column1,colum2,column3', 'column = 1')
    sql = f'SELECT {query[0]} FROM {table_name} WHERE {query[1]}'
    cur.execute(sql)
    res = cur.fetchone()
    return res


def db_insert(db_con, table_name, columns, data):
    """
    this function insert data into a specific table
    :param columns: columns that data well be added to them
    :param db_con:the connexion from database
    :param table_name: the name of the table we want to insert into
    :param data: the values we want to insert
    :return: saves the changes
    """
    cur = db_con.cursor()
    # data = (valeur1, valeur2, valeur3, ...)
    # table_name = le nom de la table par exemple ref_images
    # les colonne q'on va remplir avec les données ex "(colonne1, colonne2, colonne3)"
    sql = f'INSERT INTO {table_name}{columns} VALUES {data}'
    cur.execute(sql)
    return db_con.commit()


def db_modify(db_con, table_name, update):
    """
    this function update data in the database
    :param table_name: the name of the table
    :param db_con: the connection from the database
    :param update: the data to update on a table
    :return: saves the changes
    """
    cur = db_con.cursor()
    # table_name = le nom de la table
    # update = par exemple ('file_inode = 958634','image_id = 1')
    sql = f'UPDATE {table_name} SET {update[0]} WHERE {update[1]}'
    cur.execute(sql)
    return db_con.commit()


def db_delete(db_con, table_name, remove):
    """
    this function removes selected data from the database
    :param table_name: the name of the table
    :param db_con: the connection from the database
    :param remove: data to remove from which table
    :return: saves the changes
    """
    cur = db_con.cursor()
    # remove = (condition) par exemple ('image_id = 1')
    if remove == '*':
        sql = f"DELETE FROM {table_name}"
    else:
        sql = f"DELETE FROM {table_name} WHERE {remove}"
    cur.execute(sql)
    return db_con.commit()


def close_connection(db_con):
    """
    this function closes the connection from the database
    :param db_con: connection rom the database
    :return: closing the connection
    """
    db_con.commit()
    return db_con.close()
