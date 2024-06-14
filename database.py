import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ Create a database connection to the SQLite database specified by db_file """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connection to {db_file} established.")
        return conn
    except Error as e:
        print(e)
    return conn

def create_tables(conn):
    """ Create tables in the SQLite database """
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
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
        print("Tables created successfully.")
    except Error as e:
        print(e)

def add_user(conn, user):
    """ Add a new user to the users table """
    sql = '''INSERT INTO users(name, email, password) VALUES(?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, (user['name'], user['email'], user['password']))
    conn.commit()
    return cur.lastrowid

def get_user_by_email(conn, email):
    """ Get a user by email """
    cur = conn.cursor()
    cur.execute("SELECT id, email, password FROM users WHERE email=?", (email,))
    return cur.fetchone()

def add_transaction(conn, transaction):
    """ Add a new transaction to the transactions table """
    sql = '''INSERT INTO transactions(user_id, amount, category, date) VALUES(?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, transaction)
    conn.commit()
    return cur.lastrowid

def get_transactions(conn, user_id):
    """ Get all transactions for a specific user """
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions WHERE user_id=?", (user_id,))
    return cur.fetchall()

def delete_transaction(conn, transaction_id):
    """ Delete a transaction by transaction id """
    sql = 'DELETE FROM transactions WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (transaction_id,))
    conn.commit()

def update_transaction(conn, transaction_id, transaction):
    """ Update a transaction """
    sql = '''UPDATE transactions
             SET amount = ?,
                 category = ?,
                 date = ?
             WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, (transaction[0], transaction[1], transaction[2], transaction_id))
    conn.commit()

def get_monthly_totals(conn, user_id):
    """ Get monthly totals of income and expenses for a specific user """
    cur = conn.cursor()
    cur.execute("""
        SELECT strftime('%Y-%m', date) AS month,
               SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS income,
               SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) AS expenses
        FROM transactions
        WHERE user_id = ?
        GROUP BY month
        ORDER BY month
    """, (user_id,))
    rows = cur.fetchall()
    months = [row[0] for row in rows]
    monthly_income = [row[1] for row in rows]
    monthly_expenses = [row[2] for row in rows]
    return months, monthly_income, monthly_expenses

if __name__ == '__main__':
    database = "personal_finance.db"
    conn = create_connection(database)
    if conn is not None:
        create_tables(conn)
    else:
        print("Error! Cannot create the database connection.")