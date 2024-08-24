import sqlite3

def create_users_table():
    # Connect to the database
    conn = sqlite3.connect('tinder.db')
    cursor = conn.cursor()

    # Create the 'users' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            firstName TEXT,
            middleName TEXT,
            lastName TEXT,
            email TEXT,
            age INTEGER,
            gender TEXT,
            location TEXT,
            interests TEXT,
            password TEXT,
            min_age INT,
            max_age INT,
            location_preference INT,
            image_path TEXT
        )
    ''')

    # Commit and close the connection
    conn.commit()
    conn.close()
    return
def create_userLikes_table():
    # Connect to the database
    conn = sqlite3.connect('tinder.db')
    cursor = conn.cursor()

    # Create the userLikes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS userLikes (
        id TEXT PRIMARY KEY NOT NULL,
        userId TEXT NOT NULL,
        userLikes TEXT NOT NULL,
        dateCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE
    )
''')
    conn.commit()
    conn.close()
    return
def create_userDislikes_table():
    # Connect to the database
    conn = sqlite3.connect('tinder.db')
    cursor = conn.cursor()

    # Create the userDislikes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS userDislikes (
        id TEXT PRIMARY KEY NOT NULL,
        userId TEXT NOT NULL,
        userDislikes TEXT NOT NULL,
        dateCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE
    )
''')

    # Commit and close the connection
    conn.commit()
    conn.close()
    return
def create_userMatches_table():
    # Connect to the database
    conn = sqlite3.connect('tinder.db')
    cursor = conn.cursor()

    # Create the userMatches table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS userMatches(
        id TEXT PRIMARY KEY NOT NULL,
        user1Id TEXT NOT NULL,
        user2Id TEXT NOT NULL,
        isMatch INT NOT NULL,
        dateCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user1Id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (user2Id) REFERENCES users(id) ON DELETE CASCADE
    )
''')

    # Commit and close the connection
    conn.commit()
    conn.close()
    return
create_users_table()
create_userLikes_table()
create_userDislikes_table()
create_userMatches_table()


