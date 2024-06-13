from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_connection

class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password_hash = password
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

def get_user_by_email(email):
    conn = create_connection("personal_finance.db")
    cur = conn.cursor()
    cur.execute("SELECT id, email, password FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    if row:
        return User(row[0], row[1], row[2])
    return None

def get_user_by_id(user_id):
    conn = create_connection("personal_finance.db")
    cur = conn.cursor()
    cur.execute("SELECT id, email, password FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    if row:
        return User(row[0], row[1], row[2])
    return None