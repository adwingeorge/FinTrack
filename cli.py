import sqlite3
from database import create_connection, add_user, add_transaction, create_tables

def add_user_cli(conn):
    try:
        name = input("Enter name: ")
        email = input("Enter email: ")
        if not name or not email:
            print("Name and email cannot be empty.")
            return
        user = (name, email)
        user_id = add_user(conn, user)
        print(f"User added with ID: {user_id}")
    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def add_transaction_cli(conn):
    try:
        user_id = input("Enter user ID: ")
        if not user_id.isdigit():
            print("User ID must be a number.")
            return
        user_id = int(user_id)
        amount = input("Enter amount: ")
        if not amount.replace('.', '', 1).isdigit():
            print("Amount must be a number.")
            return
        amount = float(amount)
        category = input("Enter category: ")
        date = input("Enter date (YYYY-MM-DD): ")
        if not category or not date:
            print("Category and date cannot be empty.")
            return
        transaction = (user_id, amount, category, date)
        transaction_id = add_transaction(conn, transaction)
        print(f"Transaction added with ID: {transaction_id}")
    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main_menu():
    print("\nPersonal Finance Tracker")
    print("1. Add User")
    print("2. Add Transaction")
    print("3. Exit")
    return input("Enter choice: ")

def main():
    database = "personal_finance.db"
    conn = create_connection(database)
    if conn is not None:
        create_tables(conn)
        while True:
            choice = main_menu()
            if choice == '1':
                add_user_cli(conn)
            elif choice == '2':
                add_transaction_cli(conn)
            elif choice == '3':
                break
            else:
                print("Invalid choice. Please try again.")
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()