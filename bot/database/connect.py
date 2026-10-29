import sqlite3

DB_PATH = "data/botdata-2.db"

def get_connection():
    return sqlite3.connect(DB_PATH)