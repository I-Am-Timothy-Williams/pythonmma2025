from identity import Identity
import sqlite3
import json
import requests
from sentence_transformers import SentenceTransformer, util
import math

# Initialize/load sentence transformer model
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
    # Send geo location request to google api
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location_name}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    # Format data into latitude and longitudinal points
    if 'results' in data and len(data['results']) > 0:
        lat_lng = data['results'][0]['geometry']['location']
        return lat_lng['lat'], lat_lng['lng']
    else:
        return None, None
    
def get_interests(db_name='tinder.db', valid_user_ids=None,user_id=None):
    # If there are no valid users return an empty list
    if not valid_user_ids:
        return []

    # Get database connection
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # For each valid user, get their interests
    try:
         # Prepare the exclusion subquery
        exclusion_subquery = """
            SELECT userLikes FROM userLikes WHERE userId = ?
            UNION
            SELECT userDislikes FROM userDislikes WHERE userId = ?
        """
        
        # Construct the query string for valid_user_ids
        valid_user_ids_str = ','.join('?' * len(valid_user_ids))

        cursor.execute(f"""
            SELECT id, interests
            FROM users 
            WHERE id IN ({valid_user_ids_str})
              AND id NOT IN ({exclusion_subquery})
        """, valid_user_ids + [user_id, user_id])

        rows = cursor.fetchall()

        # We are only concerned about the interests from the rows, so that is what we are getting by taking row[0]
        interests_dict = {row[0]: row[1] for row in rows}
        interests = [interests_dict[user_id] for user_id in valid_user_ids]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        interests = []
    finally:
        conn.close()

    return interests

def get_user_interests(db_name, user_id):

    # Get database connectioin
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Get interests where id is equal to the user's id from the user table. If there is nothing in the database for that user, user_interests is None
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

    # Get users in age and location range

    users_in_range = get_users_in_age_range(db_name, user_id, min_age, max_age)

    # Turn into list of valid user ids
    valid_user_ids = [user for user in users_in_range]

    # Check for valid user ids 
    if not valid_user_ids:
        print("No valid users found.")
        return []

    # Get interests of valid users
    interests = get_interests(db_name, valid_user_ids,user_id)

    # Check for valid user interests
    if not interests:
        print("No Interest Found")
        return
    
    # Get user interests
    my_interests = get_user_interests(db_name, user_id)

    # Check for user interests
    if not my_interests:
        print(f"No interests found for user_id {user_id}")
        return
    
    # Convert user interests to list
    my_interests = [my_interests]

    # Encode all interests / get vector embbeddings for user and valid user interests
    all_embeddings = model.encode(interests, convert_to_tensor=True)
    my_embedding = model.encode(my_interests, convert_to_tensor=True)

    # Calculate cosine similarity of user vs valid user interests
    similarity_scores = util.pytorch_cos_sim(my_embedding, all_embeddings)

    # Initialize user_scores list
    user_scores =[]

    # Iterate through all users in range to append their similarity score to their id
    for i, user in enumerate(users_in_range):
        # If the user or valid users have no interests, score will automatically be 0
        if interests[i] == 'null' or my_interests[0] == 'null':
            score = 0.0
        # Else the score will equal the cosine similarity score
        else:
            score = similarity_scores[0][i].item() 

        user_scores.append((user, score))

    # Sort the order in which users show up to you based on their score
    user_scores.sort(key=lambda x: x[1], reverse=True)
    sorted_users = [user for user, score in user_scores]
    return sorted_users

        
def get_distance_between_locations(location1, location2, api_key):
    # Get lat and lng of user and valid user location
    lat1, lon1 = get_lat_lng(location1, api_key)
    lat2, lon2 = get_lat_lng(location2, api_key)
    
    # Error message if none
    if lat1 is None or lat2 is None:
        print("Error: Unable to retrieve one or both locations' latitude and longitude.")
        return None
    
    # Calculate distance using haversine formula
    return haversine(lat1, lon1, lat2, lon2)
    




def get_users_in_age_range(db_name = 'tinder.db', user_id = None, min_age=None, max_age=None,api_key="AIzaSyD6lIlT_bAI-gwi4p1nd_o95SQX62S3hW8",max_distance=None):
    # Get databasee connection
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Search for users in between age range
    try:
        
         # Construct exclusion subquery to avoid users that have been liked or disliked
        exclusion_subquery = """
            SELECT userLikes FROM userLikes WHERE userId = ?
            UNION
            SELECT userDislikes FROM userDislikes WHERE userId = ?
        """
        
        cursor.execute(f"""
            SELECT id, location
            FROM users 
            WHERE age BETWEEN ? AND ? 
              AND id NOT IN ({exclusion_subquery})
        """, (min_age, max_age, user_id, user_id))

        # Store all valid users in rows
        rows = cursor.fetchall()
        # If no valid users, return empty list
        if not rows:
            print(f"No users found in the age range {min_age} to {max_age}.")
            return []
        
        # Get user location andd location preference data
        cursor.execute("SELECT location FROM users WHERE id = ?", (user_id,))
        location = cursor.fetchone()
        cursor.execute("SELECT location_preference FROM users WHERE id = ?", (user_id,))
        max_distance = cursor.fetchone()
        
        if max_distance[0] is None:
            max_distance = [1,0]

        # Initialize final list of valid users
        result = []
        
        # Filter users that pass age range out if they do not pass location preference test

        for row in rows:
            if row[0] == user_id:
                continue
            user_distance = get_distance_between_locations(location[0], row[1], api_key)

            if int(user_distance) <= int(max_distance[0]):
                result.append(row[0])
            elif max_distance == None:
                result.append(row[0])
        
        return result
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

