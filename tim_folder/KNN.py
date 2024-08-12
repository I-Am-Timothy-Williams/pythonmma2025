import sqlite3


# =========================Need to Discuss=============================================== #


def find_most_similar_user(database_path, username):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute("SELECT interest FROM user WHERE name=?", (username,))
    user_interests = cursor.fetchall()

    if not user_interests:
        print(f"User {username} not found.")
        return None

    user_interests = set(interest[0] for interest in user_interests)

    # Find other Users interests
    cursor.execute("SELECT name, interest FROM user WHERE name != ?", (username,))
    other_users_interests = cursor.fetchall()

    # Count Users interest
    similarity_count = {}
    for other_user, interest in other_users_interests:
        if other_user not in similarity_count:
            similarity_count[other_user] = 0
        if interest in user_interests:
            similarity_count[other_user] += 1

    most_similar_user = max(similarity_count, key=similarity_count.get, default=None)

    if most_similar_user:
        print(f"The user with the most similar interests to {username} is {most_similar_user}.")
    else:
        print(f"No similar user found for {username}.")

    conn.close()

    return most_similar_user


database_path = 'tender.db'
username = 'example_user'
find_most_similar_user(database_path, username)
