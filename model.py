import pymysql
from settings import *
import sys

conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, port=MYSQL_PORT)


def init_db():
    db_query = "create database if not exists {};".format(MYSQL_DB)
    table_query = """
                create table if not exists logs(
                ip varchar(50) not null,
                url varchar(700) not null,
                version varchar(7),
                status_code int,
                time timestamp default NOW()
                );
                """
    try:
        with conn.cursor() as cursor:
            print("creating...")
            cursor.execute(db_query)
            conn.commit()
            conn.select_db(MYSQL_DB)
            cursor.execute(table_query)
            conn.commit()
            print("database and table created successfully.")
    except Exception as e:
        print(e, file=sys.stderr)
        conn.rollback()


def insert(ip, url, version, status_code):
    query = "insert into logs(ip,url,version,status_code) value('{}','{}','{}',{});".format(ip, url, version, status_code)
    try:
        with conn.cursor() as cursor:
            conn.select_db(MYSQL_DB)
            cursor.execute(query)
            conn.commit()
    except Exception as e:
        print(e, file=sys.stderr)
        conn.rollback()


if __name__ == "__main__":
    init_db()
