import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_tables(conn):
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    );
    """
    create_transactions_table = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """
    try:
        c = conn.cursor()
        c.execute(create_users_table)
        c.execute(create_transactions_table)
    except Error as e:
        print(e)
        
def add_user(conn, user):
    sql = '''INSERT INTO users(name, email) VALUES(?,?)'''
    cur = conn.cursor()
    cur.execute(sql, user)
    conn.commit()
    return cur.lastrowid

def add_transaction(conn, transaction):
    sql = '''INSERT INTO transactions(user_id, amount, category, date) VALUES(?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, transaction)
    conn.commit()
    return cur.lastrowid

if __name__ == '__main__':
    database = "personal_finance.db"
    conn = create_connection(database)
    if conn is not None:
        create_tables(conn)
    else:
        print("Error! Cannot create the database connection.")