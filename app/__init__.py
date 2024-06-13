from flask import Flask
from flask_login import LoginManager
from database import create_connection
from user import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    conn = create_connection("personal_finance.db")
    cur = conn.cursor()
    cur.execute("SELECT id, email, password FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    if row:
        return User(row[0], row[1], row[2])
    return None

from app import routes