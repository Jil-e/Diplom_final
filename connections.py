import configparser
import time
import mysql.connector
# import telebot

config = configparser.ConfigParser()
config.read("arguments.ini")


def validate(con, query):
    try:
        con.execute(query)
        return True
    except mysql.connector.OperationalError:
        return False


def connection(host, db_name, user, password):
    cnx = mysql.connector.connect(
        host=host,
        database=db_name,
        user=user,
        password=password)
    return cnx



if __name__ == '__main__':
    connection()
