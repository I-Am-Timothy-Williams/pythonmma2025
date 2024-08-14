from identity import Identity
import sqlite3
import json
from sentence_transformers import SentenceTransformer, util

def get_interests(db_name = 'tinder.db'):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT interests FROM users")
        rows = cursor.fetchall()
        interests = [row[0] for row in rows]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        interests = []
    finally:
        conn.close()

    return interests

def get_user_interests(db_name, user_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT interests FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            user_interests = row[0]
        else:
            user_interests = None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        user_interests = None
    finally:
        conn.close()

    return user_interests



def calculate_similarity(db_name='tinder.db',user_id = None):
   
    interests = get_interests(db_name)
    
    if not interests:
        print("No Interest Found")
        return
    
    my_interests = get_user_interests(db_name, user_id)

    if not my_interests:
        print(f"No interests found for user_id {user_id}")
        return
    
    my_interests = [my_interests]

    # Load Model
    model = SentenceTransformer('paraphrase-mpnet-base-v2')

    # Encode all interests
    all_embeddings = model.encode(interests, convert_to_tensor=True)
    my_embedding = model.encode(my_interests, convert_to_tensor=True)

    similarity_scores = util.pytorch_cos_sim(my_embedding, all_embeddings)


    for i in range(len(interests)):
        if interests[i] == 'null' or my_interests[0] == 'null':
            score = 0.0
        else:
            score = similarity_scores[0][i].item()  # Comparing the specific user with others
        print(f"Similarity between 'User {user_id}' with interest {my_interests[0]} and User {i + 1} with interest {interests[i]}: {score}")



def get_users_in_age_range(db_name = 'tinder.db', user_id = None, min_age=None, max_age=None):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, firstName, lastName, email, age, gender, location, interests 
            FROM users 
            WHERE age BETWEEN ? AND ?
        """, (min_age, max_age))
        
        rows = cursor.fetchall()
        if not rows:
            print(f"No users found in the age range {min_age} to {max_age}.")
            return []
        
        
        result = [row for row in rows if row[0] != user_id]

        return result
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

# Example usage
db_name = 'tinder.db'
user_id = 1  
min_age = 28
max_age = 28
users_in_range = get_users_in_age_range(db_name, user_id, min_age, max_age)

for user in users_in_range:
    print(user)


# Example usage
calculate_similarity(db_name='tinder.db', user_id=1)


