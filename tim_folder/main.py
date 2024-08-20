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

# Import the necessary modules and classes
app = FastAPI()

def get_db_connection():
    """
    Establish a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: A connection object for interacting with the SQLite database.
    """
    conn = sqlite3.connect('tinder.db')  # Update with your database file
    conn.row_factory = sqlite3.Row    
    return conn

def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.
    
    Args:
        password (str): The plain-text password to be hashed.
        
    Returns:
        str: The hashed password in hexadecimal format.
    """
    return hashlib.sha256(password.encode()).hexdigest()

class SwipeRequest(BaseModel):
    """
    A Pydantic model for handling swipe requests.
    
    Attributes:
        userId (str): The ID of the user who is swiping.
        direction (str): The direction of the swipe, either "left" or "right".
    """
    userId: str
    direction: str  # "left" or "right"

def fetch_all_users(current_user_id, conn):
    """
    Fetch all users from the database except the current user.
    
    Args:
        current_user_id (str): The ID of the current user.
        conn (sqlite3.Connection): The database connection object.
        
    Returns:
        List[dict]: A list of dictionaries containing user information.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
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

    user2 = user_profile.viewUser(userId[0])

    all_users = fetch_all_users(userId[0],get_db_connection())
    print(all_users)

    all_matches = []
    all_users2 = calculate_similarity(db_name='tinder.db', user_id=userId[0])

    for user in all_users2:
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
    print(all)

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
