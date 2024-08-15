import sqlite3
from datetime import datetime
import random
import uuid

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('tinder.db')
cursor = conn.cursor()

# Function to generate random user data
def generate_user_data():
    first_names = ['John', 'Jane', 'Alex', 'Emily', 'Chris', 'Katie', 'Mike', 'Sophie']
    last_names = ['Doe', 'Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller']
    locations = ['New York', 'Toronto', 'Los Angeles', 'Miami', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia']
    interests_list = [['reading', 'traveling'], ['sports', 'fitness'], ['music', 'technology'], ['cooking', 'art']]
    genders = ['Male', 'Female']
    emails = ['example1@gmail.com', 'example2@yahoo.com', 'example3@msn.com', 'example4@outlook.com']
    passwords = ['password1', 'password2', 'password3', 'password4']
    
    user_data = []
    
    for _ in range(10):
        user_id = str(uuid.uuid4())
        first_name = random.choice(first_names)
        middle_name = random.choice([None, "A.", "B.", "C."])
        last_name = random.choice(last_names)
        email = random.choice(emails)
        age = random.randint(20, 40)
        gender = random.choice(genders)
        location = random.choice(locations)
        interests = str(random.choice(interests_list))
        password = random.choice(passwords)
        
        user_data.append((user_id, first_name, middle_name, last_name, email, age, gender, location, interests, password))
    
    return user_data

# Function to generate random like/dislike/match data
def generate_interaction_data(table_name, user_ids):
    interaction_data = []
    
    for user_id in user_ids:
        target_user_id = random.choice(user_ids)
        while target_user_id == user_id:
            target_user_id = random.choice(user_ids)
        
        interaction_id = str(uuid.uuid4())
        date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if table_name == 'userMatches':
            is_match = random.choice([0, 1])
            interaction_data.append((interaction_id, user_id, target_user_id, is_match, date_created))
        else:
            interaction_data.append((interaction_id, user_id, target_user_id, date_created))
    
    return interaction_data

# Create tables
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
        password TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS userLikes (
        id TEXT PRIMARY KEY,
        userId TEXT,
        userLikes TEXT,
        dateCreated TEXT,
        FOREIGN KEY (userId) REFERENCES users(id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS userDislikes (
        id TEXT PRIMARY KEY,
        userId TEXT,
        userDislikes TEXT,
        dateCreated TEXT,
        FOREIGN KEY (userId) REFERENCES users(id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS userMatches (
        id TEXT PRIMARY KEY,
        user1Id TEXT,
        user2Id TEXT,
        isMatch INTEGER,
        dateCreated TEXT,
        FOREIGN KEY (user1Id) REFERENCES users(id),
        FOREIGN KEY (user2Id) REFERENCES users(id)
    )
''')

# Insert random data into the users table
user_data = generate_user_data()
cursor.executemany('''
    INSERT INTO users (id, firstName, middleName, lastName, email, age, gender, location, interests, password)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', user_data)

# Extract user ids for the interaction tables
user_ids = [user[0] for user in user_data]

# Insert random data into the userLikes, userDislikes, and userMatches tables
like_data = generate_interaction_data('userLikes', user_ids)
dislike_data = generate_interaction_data('userDislikes', user_ids)
match_data = generate_interaction_data('userMatches', user_ids)

cursor.executemany('''
    INSERT INTO userLikes (id, userId, userLikes, dateCreated)
    VALUES (?, ?, ?, ?)
''', like_data)

cursor.executemany('''
    INSERT INTO userDislikes (id, userId, userDislikes, dateCreated)
    VALUES (?, ?, ?, ?)
''', dislike_data)

cursor.executemany('''
    INSERT INTO userMatches (id, user1Id, user2Id, isMatch, dateCreated)
    VALUES (?, ?, ?, ?, ?)
''', match_data)

# Commit changes and close the connection
conn.commit()
conn.close()

# Summary of actions
{
    "users_inserted": len(user_data),
    "likes_inserted": len(like_data),
    "dislikes_inserted": len(dislike_data),
    "matches_inserted": len(match_data)
}
