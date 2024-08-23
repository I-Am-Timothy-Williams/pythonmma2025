from identity import Identity
import sqlite3
import json
import requests
from sentence_transformers import SentenceTransformer, util
import math
model = SentenceTransformer('paraphrase-mpnet-base-v2')

def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Difference in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = R * c

    return distance

def get_lat_lng(location_name, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location_name}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if 'results' in data and len(data['results']) > 0:
        lat_lng = data['results'][0]['geometry']['location']
        return lat_lng['lat'], lat_lng['lng']
    else:
        return None, None

# def get_interests(db_name = 'tinder.db',user_id= None,min_age=None, max_age=None,valid_id=None):

#     conn = sqlite3.connect(db_name)
#     cursor = conn.cursor()

#     try:
#         print(min_age,max_age)
#         cursor.execute("SELECT interests FROM users WHERE id != ? AND age between ? and ?", (user_id, min_age,max_age))
#         rows = cursor.fetchall()
#         interests = [row[0] for row in rows]
#     except sqlite3.Error as e:
#         print(f"Database error: {e}")
#         interests = []
#     finally:
#         conn.close()

#     return interests
def get_interests(db_name='tinder.db', valid_user_ids=None):
    if not valid_user_ids:
        return []

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        # cursor.execute("SELECT interests FROM users WHERE id IN ({})".format(
        #     ','.join('?' for _ in valid_user_ids)), valid_user_ids)
        cursor.execute("SELECT interests FROM users WHERE id IN ({})".format(
        ','.join('?' * len(valid_user_ids))
    ),
    valid_user_ids
)#Potential issue of interests getting ordered inversely
        rows = cursor.fetchall()
        interests = [row[0] for row in rows]
        print(interests[0])
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



def calculate_similarity(db_name='tinder.db',user_id = None,min_age=None,max_age=None):
   
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()


    # cursor.execute("SELECT * FROM users WHERE id != ?",(user_id,))
    # users = cursor.fetchall()

    users_in_range = get_users_in_age_range(db_name, user_id, min_age, max_age)
    print(users_in_range)
    valid_user_ids = [user for user in users_in_range]

    if not valid_user_ids:
        print("No valid users found.")
        return []

    interests = get_interests(db_name, valid_user_ids)
    if not interests:
        print("No Interest Found")
        return
    
    my_interests = get_user_interests(db_name, user_id)

    if not my_interests:
        print(f"No interests found for user_id {user_id}")
        return
    
    my_interests = [my_interests]

    # Load Model

    # Encode all interests
    all_embeddings = model.encode(interests, convert_to_tensor=True)
    my_embedding = model.encode(my_interests, convert_to_tensor=True)

    similarity_scores = util.pytorch_cos_sim(my_embedding, all_embeddings)
    user_scores =[]

    for i, user in enumerate(users_in_range):
        # print(i,interests)
        if interests[i] == 'null' or my_interests[0] == 'null':
            score = 0.0
        else:
            score = similarity_scores[0][i].item()  # Comparing the specific user with others
        user_scores.append((user, score))
        # print(f"Similarity between 'User {user_id}' with interest {my_interests[0]} and User {i + 1} with interest {interests[i]}: {score}")
    user_scores.sort(key=lambda x: x[1], reverse=True)
    sorted_users = [user for user, score in user_scores]
    print(sorted_users)
    return sorted_users


        
        
def get_distance_between_locations(location1, location2, api_key):
    lat1, lon1 = get_lat_lng(location1, api_key)
    lat2, lon2 = get_lat_lng(location2, api_key)
    
    if lat1 is None or lat2 is None:
        print("Error: Unable to retrieve one or both locations' latitude and longitude.")
        return None
    
    return haversine(lat1, lon1, lat2, lon2)
    




def get_users_in_age_range(db_name = 'tinder.db', user_id = None, min_age=None, max_age=None,api_key="AIzaSyD6lIlT_bAI-gwi4p1nd_o95SQX62S3hW8",max_distance=None):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id,location
            FROM users 
            WHERE age BETWEEN ? AND ?
        """, (min_age, max_age))
        print('hi')
        rows = cursor.fetchall()
        if not rows:
            print(f"No users found in the age range {min_age} to {max_age}.")
            return []
        cursor.execute("SELECT location FROM users WHERE id = ?", (user_id,))
        location = cursor.fetchone()
        cursor.execute("SELECT location_preference FROM users WHERE id = ?", (user_id,))
        max_distance = cursor.fetchone()
        
        result = []
        


        for row in rows:
            if row[0] == user_id:
                continue
            user_distance = get_distance_between_locations(location[0], row[1], api_key)

            if int(user_distance) <= int(max_distance[0]):
                result.append(row[0])
            elif max_distance == None:
                result.append(row[0])
        # result = [row for row in rows if row[0] != user_id]
        
        return result
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

