from fastapi import FastAPI, Request, Form, HTTPException, Body
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from user import UserProfile
from user_interaction import UserInteraction
import sqlite3
from pydantic import BaseModel
import hashlib
from urllib.parse import urlencode
from typing import List
import json
from similarity_score import *
import requests


app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect('tinder.db')  # Update with your database file
    conn.row_factory = sqlite3.Row    
    return conn

def hash_password(password: str) -> str:
    # Hashing the password for comparison
    return hashlib.sha256(password.encode()).hexdigest()

def get_lat_lng(location_name, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location_name}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if 'results' in data and len(data['results']) > 0:
        lat_lng = data['results'][0]['geometry']['location']
        return lat_lng['lat'], lat_lng['lng']
    else:
        return None, None

class SwipeRequest(BaseModel):
    userId: str
    direction: str  # "left" or "right"

def fetch_all_users(current_user_id, conn,min_age,max_age):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE age BETWEEN ? AND ?",(min_age,max_age))
    users = cursor.fetchall()

    all_users = []
    for user in users:
        if user['id'] == current_user_id:
            continue  # Skip the current user's row

        interests_array = json.loads(user['interests']) if isinstance(user['interests'], str) else user['interests']
        if interests_array is None:
            interests_array = ["None"]
        
        all_users.append({
            "firstName": user['firstName'],
            "lastName": user['lastName'],
            "gender": user['gender'],
            "age": user['age'],
            "location": user['location'],
            "email": user['email'],
            "interests": interests_array,
        })
    return all_users

def fetch_all_matches(current_user_id, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM userMatches")
    users = cursor.fetchall()

    all_matches = []
    for user in users:
        if user['user1Id'] != current_user_id:
            if user['user2Id'] != current_user_id:
                continue  # Skip the current user's row

        

        if user['user1Id'] == current_user_id:
            cursor.execute("SELECT * FROM users WHERE id = ?",(user['user2Id'],))
            match = cursor.fetchone()
        else:
            cursor.execute("SELECT * FROM users WHERE id = ?",(user['user1Id'],))
            match = cursor.fetchone()
        
        interests_array = json.loads(match['interests']) if isinstance(match['interests'], str) else match['interests']
        if interests_array is None:
            interests_array = ["None"]

        all_matches.append({
            "firstName": match['firstName'],
            "lastName": match['lastName'],
            "gender": match['gender'],
            "age": match['age'],
            "location": match['location'],
            "email": match['email'],
            "interests": interests_array,
        })
    return all_matches



# Mount the static directory
app.mount("/tim_folder/static", StaticFiles(directory="tim_folder/static"), name="static")

# Setup Jinja2 template engine
templates = Jinja2Templates(directory="tim_folder/templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.post("/")
async def login(
    email: str = Form(...),
    password: str = Form(...)
):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to check if the user exists and the password matches
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    cursor.execute("SELECT interests FROM users WHERE email = ?", (email,))
    interest=cursor.fetchone()
    # print(interest[0]=="null")
    conn.close()

    if user:
        success_message = urlencode({"message": "Login successful"})        
        if interest[0] != "null":
            response=RedirectResponse(url="/dashboard", status_code=302)
            response.set_cookie(key="email", value=email)
            return response
        else:
            response=RedirectResponse(url="/submit-interests", status_code=302)
            response.set_cookie(key="email",value=email)
            return response
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")

@app.get("/register")
def read_root(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(
    request: Request,
    firstName: str = Form(...),
    lastName: str = Form(...),
    email: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    location: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    interests: str = Form(None)
):
    # Create an instance of your UserProfile class
    user_profile = UserProfile()

    # Call the create_user_profile method with the form data
    userData = {
    'firstName':firstName,
    'middleName': None, 
    'lastName': lastName,
    'email': email,
    'age': age,
    'gender': gender,   
    'location': location,
    'interests': interests,
    'password': password
    }
    user_profile.createUser(userData)

    # Optionally, you can pass a success message back to the template
    return RedirectResponse(url="/", status_code=302)

@app.get("/dashboard")
async def dashboard(request: Request):
    email = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    userId = cursor.fetchone()
    user_profile = UserProfile()
    cursor.execute("SELECT min_age FROM users WHERE email = ?", (email,))
    min_age = cursor.fetchone()
    cursor.execute("SELECT max_age FROM users WHERE email = ?", (email,))
    max_age = cursor.fetchone()

    user2 = user_profile.viewUser(userId[0])

    # all_users = fetch_all_users(userId[0],get_db_connection(),min_age[0],max_age[0])
    # print(all_users)

    all_matches = []
    all_users2 = calculate_similarity(db_name='tinder.db', user_id=userId[0],min_age=min_age[0],max_age=max_age[0])

    for user in all_users2:
        cursor.execute("SELECT * FROM users WHERE id = ?",(user,))
        user=cursor.fetchone()
        interests_array = json.loads(user[8]) if isinstance(user[8], str) else user[8]

        if interests_array is None:
            interests_array = ["None"]
        all_matches.append({
            "firstName": user[1],
            "lastName": user[3],
            "gender": user[6],
            "age": user[5],
            "location": user[7],
            "email": user[4],
            "interests": interests_array,
        })
    return templates.TemplateResponse("dashboard.html", {"request": request,"all_users":all_matches, "user": user2, "message": "User logged in successfully"})
@app.post("/dashboard")
async def get_users(
    request: Request,
    firstName: str = Form(...),
    lastName: str = Form(...),
    email: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    location: str = Form(...),
    interests: str = Form(...)):

    user_profile = UserProfile()

    interests_list = [interest.strip() for interest in interests.split(',')]
    interests_json = json.dumps(interests_list)

    # Call the create_user_profile method with the form data
    userData = {
    'firstName':firstName,
    'middleName': None, 
    'lastName': lastName,
    'email': email,
    'age': age,
    'gender': gender,   
    'location': location,
    'interests': interests_json,
    }

    email = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    userId = cursor.fetchone()
    user_profile.editUser(userId[0],userData)

    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/submit-interests")
async def interests(request: Request):
    return templates.TemplateResponse("interests.html", {"request": request, "message": "Select your interests"})

@app.post("/submit-interests")
async def update_user_interests(
    request: Request,
    interests: List[str] = Form(...),
):

    interests = interests[0]

    # Split the string by commas
    interests = interests.split(',')
    print(interests)


    user_profile = UserProfile()

    userData = {
        'interests': interests
    }

    email = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    userId = cursor.fetchone()
    
    user_profile.editUser(userId[0],userData)
    return RedirectResponse(url="/dashboard", status_code=302)

@app.post("/swipe")
async def handle_swipe(request: Request, direction: str = Body(...), email: str = Body(...)):
    # Handle the swipe logic (e.g., save to database)
    userEmail = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (userEmail,))
    userId = cursor.fetchone()

    user_interaction = UserInteraction()

    if direction == "right":
        # Handle like logic
        print(direction,email)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        likedUserId = cursor.fetchone()
        user_interaction.likeUser(userId[0],likedUserId[0])

    elif direction == "left":
        # Handle dislike logic
        print(direction,email)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        dislikedUserId = cursor.fetchone()
        user_interaction.dislikeUser(userId[0],dislikedUserId[0])
        pass

    return {"message": "Swipe registered successfully"}

@app.get("/matches")
async def view_matches(request:Request):
    userEmail = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (userEmail,))
    userId = cursor.fetchone()
    all_matches = fetch_all_matches(userId[0],get_db_connection())
    print(all_matches)

    return templates.TemplateResponse("matches.html", {"all_matches":all_matches, "request": request, "message": "View your matches"})

@app.post("/delete-profile")
async def delete_user(request:Request):
    user_profile = UserProfile()
    userEmail = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (userEmail,))
    userId = cursor.fetchone()
    user_profile.deleteUser(userId[0])
    return RedirectResponse(url="/", status_code=302)

@app.get("/set-location-preference")
async def set_location_preference(request: Request):
    userEmail = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT location_preference FROM users WHERE email = ?", (userEmail,))
    preference = cursor.fetchone()
    cursor.execute("SELECT location FROM users WHERE email = ?", (userEmail,))
    location = cursor.fetchone()

     # Check if the preference is null and set it to 1 if so
    if preference is None or preference[0] is None:
        preference_value = 1
    else:
        preference_value = preference[0]

    if location[0] is None:
        location_name = "New York"  # Default to New York
        lat, lng = get_lat_lng(location_name, "AIzaSyD6lIlT_bAI-gwi4p1nd_o95SQX62S3hW8")
        if lat is None or lng is None:
            lat, lng = 40.749933, -73.98633  # Default to New York
    else:
        lat, lng = get_lat_lng(location[0], "AIzaSyD6lIlT_bAI-gwi4p1nd_o95SQX62S3hW8")

    return templates.TemplateResponse("location_preference.html", {"lat":lat,"lng":lng,"preference":preference_value,"request": request})

@app.post("/set-location-preference")
async def update_location_preference(
    request: Request,
    preferences: int = Form(..., alias='preferences'),
):
    print(preferences)
    user_profile = UserProfile()
    email = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    userId = cursor.fetchone()

    # Update the user's location preference in the database
    location_preference_data = {
        'location_preference': preferences
    }

    user_profile.editUser(userId[0], location_preference_data)
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/set-age-preference")
async def set_age_preference(request: Request):
    return templates.TemplateResponse("age_preference.html", {"request": request})

@app.post("/set-age-preference")
async def update_age_preference(
    request: Request,
    min_age: int = Form(..., alias="minAge"),
    max_age: int = Form(..., alias="maxAge"),
):
    # Debugging: Print the received values
    print(f"Received min_age: {min_age}, max_age: {max_age}")
    
    user_profile = UserProfile()
    email = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    userId = cursor.fetchone()

    # Update the user's age preference in the database
    age_preference_data = {
        'min_age': min_age,
        'max_age': max_age
    }

    user_profile.editUser(userId[0], age_preference_data)

    return RedirectResponse(url="/dashboard", status_code=302)


