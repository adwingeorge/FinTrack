from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from user import User, get_user_by_email, get_user_by_id
from app import app
from database import create_connection, add_user, add_transaction

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        conn = create_connection("personal_finance.db")
        if conn is not None:
            user = get_user_by_email(email)
            if user:
                flash("Email already registered. Please use a different email address.")
                return redirect(url_for('register'))
            add_user(conn, {'name': name, 'email': email, 'password': password})
            flash("Registration successful! Please log in.")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user_by_email(email)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = create_connection("personal_finance.db")
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT SUM(amount) FROM transactions WHERE amount > 0")
        total_income = cur.fetchone()[0] or 0
        cur.execute("SELECT SUM(amount) FROM transactions WHERE amount < 0")
        total_expenses = cur.fetchone()[0] or 0
        current_balance = total_income + total_expenses

        cur.execute("""
            SELECT category, SUM(amount)
            FROM transactions
            WHERE amount < 0
            GROUP BY category
        """)
        expenses_by_category = cur.fetchall()
        categories = ['Rent', 'Groceries', 'Utilities', 'Entertainment', 'Miscellaneous']
        category_expenses = [0] * len(categories)
        for category, amount in expenses_by_category:
            if category in categories:
                index = categories.index(category)
                category_expenses[index] = abs(amount)

        return render_template('dashboard.html', total_income=total_income, total_expenses=abs(total_expenses), current_balance=current_balance, expenses_by_category=category_expenses)
    return render_template('dashboard.html', total_income=0, total_expenses=0, current_balance=0, expenses_by_category=[])

@app.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction_route():
    categories = ['Rent', 'Groceries', 'Utilities', 'Entertainment', 'Miscellaneous']
    if request.method == 'POST':
        user_id = current_user.id
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']
        conn = create_connection("personal_finance.db")
        if conn is not None:
            add_transaction(conn, (user_id, amount, category, date))
        return redirect(url_for('dashboard'))
    return render_template('add_transaction.html', categories=categories)