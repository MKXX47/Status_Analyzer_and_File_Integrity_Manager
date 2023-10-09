
CREATE TABLE fim_rules
(
    fim_rule_id   integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    fim_rule_name VARCHAR(256),
    path          VARCHAR(256),
    start_inode   INTEGER,
    inode         BOOLEAN,
    parent        BOOLEAN,
    name          BOOLEAN,
    type          BOOLEAN,
    mode          BOOLEAN,
    nlink         BOOLEAN,
    uid           BOOLEAN,
    gid           BOOLEAN,
    size          BOOLEAN,
    atime         BOOLEAN,
    mtime         BOOLEAN,
    md5           BOOLEAN,
    sha1          BOOLEAN,
    schedule    INTEGER
);








create table sa_jobs
(
    sa_job_id       integer NOT NULL PRIMARY KEY AUTOINCREMENT ,
    sa_job_name     VARCHAR(256),
    script          BOOLEAN,
    command_script  VARCHAR(256),
    expected_result VARCHAR(256),
    alert_message   VARCHAR(256),
    schedule    INTEGER
);




CREATE TABLE client
(
    client_id integer NOT NULL PRIMARY KEY autoincrement ,
    hostname Varchar(256)

);


CREATE TABLE client_sa
(
    client_id integer,
    sa_job_id integer,
    FOREIGN KEY (sa_job_id) REFERENCES sa_jobs(sa_job_id)

);


CREATE TABLE client_fim
(
    client_id integer,
    fim_rule_id integer,
    FOREIGN KEY (client_id) REFERENCES client(client_id),
    FOREIGN KEY (fim_rule_id) REFERENCES fim_rules(fim_rule_id)

);

CREATE TABLE fim_events
(
    fim_event_id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    datetime_event TIMESTAMP,
    except_msg     VARCHAR(256),
    except_active  BOOLEAN,
    file_inode     int,
    image_id       int,
    fim_rule_id   integer,
    FOREIGN KEY (fim_rule_id) References fim_rules (fim_rule_id)
);

CREATE TABLE sa_events
(
    sa_event_id    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    datetime_event TIMESTAMP,
    except_active  BOOLEAN,
    sa_job_id       integer,    FOREIGN KEY (sa_job_id) References sa_jobs (sa_job_id)

);