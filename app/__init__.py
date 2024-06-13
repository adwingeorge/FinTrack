from flask import Flask
from database import create_connection, create_tables

app = Flask(__name__)

# Initialize the database
with app.app_context():
    conn = create_connection("personal_finance.db")
    if conn is not None:
        create_tables(conn)

from app import routes