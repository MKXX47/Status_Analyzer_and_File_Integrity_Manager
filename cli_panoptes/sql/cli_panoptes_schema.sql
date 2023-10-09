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
    schedule     INTEGER
);


create table stat_files
(
    file_inode INTEGER PRIMARY KEY ,
    parent_id  INTEGER,
    file_name  VARCHAR(256),
    file_type  varchar(256),
    file_mode  VARCHAR(256),
    file_nlink INTEGER,
    file_uid   INTEGER,
    file_gid   INTEGER,
    file_size  INTEGER,
    file_atime TIMESTAMP,
    file_mtime TIMESTAMP,
    file_ctime TIMESTAMP,
    file_md5   VARCHAR(32),
    file_SHA1  VARCHAR(40)
);



create table ref_images
(
    image_id       int,
    file_inode     int,
    datetime_image timestamp,
    parent_id      int,
    file_name      varchar(256),
    file_type      varchar(256),
    file_mode      varchar(256),
    file_nlink     int,
    file_uid       int,
    file_gid       int,
    file_size      int,
    file_atime     TIMESTAMP,
    file_mtime     TIMESTAMP,
    file_ctime     TIMESTAMP,
    file_md5       varchar(32),
    file_SHA1      varchar(40)
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
    FOREIGN KEY (file_inode) References stat_files (file_inode),
    FOREIGN KEY (image_id) References ref_images (image_id),
    FOREIGN KEY (fim_rule_id) References fim_rules (fim_rule_id)
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



CREATE TABLE sa_events
(
    sa_event_id    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    datetime_event TIMESTAMP,
    except_active  BOOLEAN,
    sa_job_id       integer,    FOREIGN KEY (sa_job_id) References sa_jobs (sa_job_id)

);


CREATE TABLE fim_image
(
    fim_rule_id   integer,
    image_id       integer,
    file_inode integer,
    FOREIGN KEY (fim_rule_id) References fim_rules (fim_rule_id),
    FOREIGN KEY (image_id) References ref_images (image_id)
);