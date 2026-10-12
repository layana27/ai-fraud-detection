import sqlite3


def create_database():
    connection = sqlite3.connect("fraud_transactions.db")
    cursor = connection.cursor()

    # Store checked transactions.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            transaction_type TEXT,
            location TEXT,
            result TEXT
        )
    """)

    # Store registered user accounts.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    print("Database created successfully!")
