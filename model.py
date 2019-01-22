import pymysql
from settings import *
import sys

conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, port=MYSQL_PORT, db=MYSQL_DB)


def init_db():
    db_query = "create database if not exists drupal_version;"
    table_query = """
                create table if not exists logs(
                ip varchar(50) not null,
                url varchar(700) not null,
                version varchar(7),
                status_code int,
                constraint pk1 PRIMARY KEY (ip,url)
                );
                """
    try:
        with conn.cursor() as cursor:
            cursor.execute(db_query)
            conn.commit()
            cursor.execute(table_query)
            conn.commit()
            print("database and table created successfully.")
    except Exception as e:
        print(e, file=sys.stderr)
        conn.rollback()


def insert(ip, url, version, status_code):
    query = f"insert into logs value({ip},{url},{version},{status_code});"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            conn.commit()
    except Exception as e:
        print(e, file=sys.stderr)
        conn.rollback()

if __name__=="__name__":
    init_db()