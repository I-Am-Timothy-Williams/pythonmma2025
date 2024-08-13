from identity import Identity
import sqlite3
import json
from sentence_transformers import SentenceTransformer, util

def get_interests(db_name = 'tinder.db'):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT interest FROM user")
        rows = cursor.fetchall()
        interests = [row[0] for row in rows]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        interests = []
    finally:
        conn.close()

    return interests

def calculate_similarity(db_name='tinder.db'):
   
    interests = get_interests(db_name)
    
    if not interests:
        print("No Interest Found")
        return

    # Load Model
    model = SentenceTransformer('paraphrase-mpnet-base-v2')


    embeddings = model.encode(interests, convert_to_tensor=True)

    similarity_scores = util.pytorch_cos_sim(embeddings, embeddings)

    for i in range(len(interests)):
        for j in range(i + 1, len(interests)):
            print(f"Similarity between '{interests[i]}' and '{interests[j]}': {similarity_scores[i][j].item()}")

