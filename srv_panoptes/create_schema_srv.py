import os
import sqlite3

DB_FILENAME = './data/srv_panoptes.sqlite'
SCHEMA_FILENAME = './sql/srv_panoptes_schema.sql'
db_is_new = not os.path.exists(DB_FILENAME)
with sqlite3.connect(DB_FILENAME, uri=True) as conn:
    if db_is_new:
        print('Creating schema')
    with open(SCHEMA_FILENAME, 'rt') as f:
        schema = f.read()
    conn.executescript(schema)
