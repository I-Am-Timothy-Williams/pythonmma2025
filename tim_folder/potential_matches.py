import sqlite3
import pandas as pd


def find_users_with_same_location(database_path, username):
    # Data set up
    conn = sqlite3.connect(database_path)
    user_df = pd.read_sql_query("SELECT * FROM user", conn)
    conn.close()

    # Check user exist
    if username not in user_df['name'].values:
        print(f"User {username} not found.")
        return []

    # Find User's location
    user_location = user_df[user_df['name'] == username]['location'].values[0]

    # Find Same location
    same_location_users = user_df[user_df['location'] == user_location]
    same_location_users = same_location_users[same_location_users['name'] != username]

    if not same_location_users.empty:
        print(
            f"Users with the same location as {username} ({user_location}): {', '.join(same_location_users['name'].values)}")
    else:
        print(f"No users found with the same location as {username}.")

    return same_location_users['name'].values


