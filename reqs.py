import configparser

config = configparser.ConfigParser()
config.read("arguments.ini")

def show_tables(db_name):
    tables_showing = f"SHOW TABLES from `{db_name}`"
    return tables_showing

def coloms(name_table):
    exit = f"SHOW FIELDS FROM `{name_table}`"
    return exit