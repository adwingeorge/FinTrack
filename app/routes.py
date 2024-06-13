from flask import render_template, request, redirect, url_for
from app import app
from database import create_connection, add_user, add_transaction

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user_route():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        conn = create_connection("personal_finance.db")
        if conn is not None:
            add_user(conn, (name, email))
        return redirect(url_for('index'))
    return render_template('add_user.html')

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction_route():
    if request.method == 'POST':
        user_id = request.form['user_id']
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']
        conn = create_connection("personal_finance.db")
        if conn is not None:
            add_transaction(conn, (user_id, amount, category, date))
        return redirect(url_for('index'))
    return render_template('add_transaction.html')