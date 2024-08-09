import sqlite3

def create_users_table():
    # Connect to the database
    conn = sqlite3.connect('tinder.db')
    cursor = conn.cursor()

    # Create the 'users' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            userId TEXT PRIMARY KEY,
            firstName TEXT,
            middleName TEXT,
            lastName TEXT,
            email TEXT,
            age INTEGER,
            gender TEXT,
            location TEXT,
            interests TEXT
        )
    ''')

    # Commit and close the connection
    conn.commit()
    conn.close()
create_users_table()