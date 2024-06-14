from flask import render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from database import create_connection, add_user, add_transaction, get_user_by_email, get_transactions, delete_transaction, update_transaction, get_monthly_totals
import sqlite3

DATABASE = 'personal_finance.db'

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User:
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    print(f"Loading user with ID: {user_id}")
    conn = create_connection(DATABASE)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT id, email, password FROM users WHERE id=?", (user_id,))
        user_data = cur.fetchone()
        print(f"User data loaded: {user_data}")
        if user_data:
            return User(user_data[0], user_data[1], user_data[2])
        return None

@app.route('/')
@login_required
def dashboard():
    print("Accessing dashboard")
    conn = create_connection(DATABASE)
    with conn:
        transactions = get_transactions(conn, current_user.id)
        total_income, total_expenses, current_balance = 0, 0, 0
        for transaction in transactions:
            if transaction[2] > 0:
                total_income += transaction[2]
            else:
                total_expenses += abs(transaction[2])
        current_balance = total_income - total_expenses

        months, monthly_income, monthly_expenses = get_monthly_totals(conn, current_user.id)

    return render_template('dashboard.html', total_income=total_income, total_expenses=total_expenses,
                           current_balance=current_balance, transactions=transactions,
                           months=months, monthly_income=monthly_income, monthly_expenses=monthly_expenses)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(f"Trying to login with email: {email}")
        conn = create_connection(DATABASE)
        with conn:
            user_data = get_user_by_email(conn, email)
            print(f"User data retrieved: {user_data}")
            if user_data and check_password_hash(user_data[2], password):
                user = User(user_data[0], user_data[1], user_data[2])
                login_user(user)
                print("Login successful")
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password')
                print("Login failed")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        conn = create_connection(DATABASE)
        try:
            with conn:
                add_user(conn, {'name': name, 'email': email, 'password': password})
            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered. Please use a different email.')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    print("Logged out")
    return redirect(url_for('login'))

@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense_route():
    amount = -float(request.form['amount'])
    category = request.form['category']
    date = f"{request.form['year']}-{request.form['month']}-01"
    conn = create_connection(DATABASE)
    with conn:
        add_transaction(conn, (current_user.id, amount, category, date))
    return redirect(url_for('dashboard'))

@app.route('/add_income', methods=['POST'])
@login_required
def add_income_route():
    amount = float(request.form['amount'])
    date = f"{request.form['year']}-{request.form['month']}-01"
    conn = create_connection(DATABASE)
    with conn:
        add_transaction(conn, (current_user.id, amount, 'Income', date))
    return redirect(url_for('dashboard'))

@app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction_route(transaction_id):
    conn = create_connection(DATABASE)
    with conn:
        delete_transaction(conn, transaction_id)
    return redirect(url_for('dashboard'))

@app.route('/edit_transaction/<int:transaction_id>', methods=['POST'])
@login_required
def edit_transaction_route(transaction_id):
    amount = float(request.form['amount'])
    category = request.form['category']
    date = f"{request.form['year']}-{request.form['month']}-01"
    conn = create_connection(DATABASE)
    with conn:
        update_transaction(conn, transaction_id, (amount, category, date))
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)