from fastapi import FastAPI, Request, Form, HTTPException, Body, UploadFile, File, Response
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
import identity
import os
import requests


app = FastAPI()

UPLOAD_DIRECTORY = "tim_folder/static"


def get_db_connection():
    # Establish database connection
    conn = sqlite3.connect('tinder.db') 
    conn.row_factory = sqlite3.Row    
    return conn

def hash_password(password: str) -> str:
    # Hashing the password for comparison
    return hashlib.sha256(password.encode()).hexdigest()

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

class SwipeRequest(BaseModel):
    # Use Pydantic Model to fetch swipe data from dashboard.html
    userId: str
    direction: str  # "left" or "right"

def fetch_all_matches(current_user_id, conn):
    #Fetch all users from userMatches table
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM userMatches")
    users = cursor.fetchall()

    #Include only rows with user id in it
    all_matches = []
    for user in users:
        if user['user1Id'] != current_user_id:
            if user['user2Id'] != current_user_id:
                continue  # Skip the current user's row

        
        #Fetch the matched user id

        if user['user1Id'] == current_user_id:
            cursor.execute("SELECT * FROM users WHERE id = ?",(user['user2Id'],))
            match = cursor.fetchone()
        else:
            cursor.execute("SELECT * FROM users WHERE id = ?",(user['user1Id'],))
            match = cursor.fetchone()

        #Fetch matched user interests
        
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
            "image_path": match['image_path'],
        })
    return all_matches



# Mount the static directory
app.mount("/tim_folder/static", StaticFiles(directory="tim_folder/static"), name="static")

# Setup Jinja2 template engine
templates = Jinja2Templates(directory="tim_folder/templates")


"""
For our GUI we are hosting a website on our local machine using FastAPI as a framework. 
We interact with various pages using GET and POST requests. The page that is being interacted with is what is enclosed 
in the brackets. E.g. app.get('/dashboard') is handling the GET requests that are being sent to 127.0.0.1:8000/dashboard

GET Requests
Purpose: Used to retrieve data from the server.

How It Works:

The client sends a GET request to a specified endpoint (URL).
The server processes the request and returns the requested data.
Typically, GET requests do not modify any data on the server; they are read-only.

POST Requests
Purpose: Used to send data to the server, often for creating or updating resources.

How It Works:

The client sends a POST request to the server, usually with data in the body of the request.
The server processes the data and performs some action, like saving the data to a database.
The server then typically returns a response indicating the success or failure of the operation.
"""


@app.get("/")
def read_root(request: Request):
     # Renders the login/index page when a GET request is made to "/"
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
async def login(
    email: str = Form(...),
    password: str = Form(...)
):
    # Get database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to check if the user exists and the password matches
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()

    # Fetch interests from user
    cursor.execute("SELECT interests FROM users WHERE email = ?", (email,))
    interest=cursor.fetchone()
    conn.close()
    
    #Error Handling for incorrect information
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
    # Renders the registration page when a GET request is made to "/register"
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
    """
    Handles user registration by accepting form data, creating a new user profile, 
    and storing the user information in the database.
    """

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
    # Retrieve user email from cookies and get profile information from database
    email = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    # Fetch user id, min and max age requirements
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    userId = cursor.fetchone()
    user_profile = UserProfile()
    cursor.execute("SELECT min_age FROM users WHERE email = ?", (email,))
    min_age = cursor.fetchone()
    cursor.execute("SELECT max_age FROM users WHERE email = ?", (email,))
    max_age = cursor.fetchone()

    # Fetch user information
    my_user = user_profile.viewUser(userId[0])

    all_matches = []

    # Fetch all users that fit within age and location restraints
    all_users = calculate_similarity(db_name='tinder.db', user_id=userId[0],min_age=min_age[0],max_age=max_age[0])

    # For each valid user, store their information in a list
    for user in all_users:
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
    return templates.TemplateResponse("dashboard.html", {"request": request,"all_users":all_matches, "user": my_user, "message": "User logged in successfully"})
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

    # Call the edit_user_profile method with the form data
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
    # Visualize interests.html
    return templates.TemplateResponse("interests.html", {"request": request, "message": "Select your interests"})

@app.post("/submit-interests")
async def update_user_interests(
    request: Request,
    interests: List[str] = Form(...),
):


    # Fetch and store interests as a list of interests which updates the user profile usingi edit_user_profile function
    interests = interests[0]

    interests = interests.split(',')

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
    # Redirect user to dashboard once interests are submitted
    return RedirectResponse(url="/dashboard", status_code=302)

@app.post("/swipe")
async def handle_swipe(request: Request, direction: str = Body(...), email: str = Body(...)):

    # Fetch my user id

    userEmail = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (userEmail,))
    userId = cursor.fetchone()

    user_interaction = UserInteraction()

    # Handle the swipe logic

    if direction == "right":
        # Handle like logic (calls the like_user user_interaction function)
        cursor = conn.cursor()
        # Fetch the liked user
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        likedUserId = cursor.fetchone()
        user_interaction.likeUser(userId[0],likedUserId[0])

    elif direction == "left":
        # Handle dislike logic (calls the dislike_user user_interaction function)
        cursor = conn.cursor()
        # Fetch the disliked user
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        dislikedUserId = cursor.fetchone()
        user_interaction.dislikeUser(userId[0],dislikedUserId[0])
        pass

    return {"message": "Swipe registered successfully"}

@app.get("/matches")
async def view_matches(request:Request):

    # Fetch user id
    userEmail = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (userEmail,))
    userId = cursor.fetchone()

    # Get all match data to send to matches.html template to display
    all_matches = fetch_all_matches(userId[0],get_db_connection())

    return templates.TemplateResponse("matches.html", {"all_matches":all_matches, "request": request, "message": "View your matches"})

@app.post("/delete-profile")
async def delete_user(request:Request):

    user_profile = UserProfile()

    # Fetch user id
    userEmail = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (userEmail,))
    userId = cursor.fetchone()

    # Delete user profile using delete_user_profile function
    user_profile.deleteUser(userId[0])

    # Redirect you to login page
    return RedirectResponse(url="/", status_code=302)

@app.get("/set-location-preference")
async def set_location_preference(request: Request):

    # Fetch user email to retrieve location and location preference information
    userEmail = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT location_preference FROM users WHERE email = ?", (userEmail,))
    preference = cursor.fetchone()
    cursor.execute("SELECT location FROM users WHERE email = ?", (userEmail,))
    location = cursor.fetchone()

    # Check if the preference is null and set it to 1 if so (Essentially default value is 1 km), Otherwise it uses value from database.
    if preference is None or preference[0] is None:
        preference_value = 1
    else:
        preference_value = preference[0]

    # If you have no location set, default location is New York
    if location[0] is None:
        location_name = "New York"  # Default to New York
        lat, lng = get_lat_lng(location_name, "api_key")
        # If for whatever reason you cannot retrieve lat, lng, default to New York lat and lng.
        if lat is None or lng is None:
            lat, lng = 40.749933, -73.98633  # Default to New York
    else:
    # Else find lat and lng from location from the database
        lat, lng = get_lat_lng(location[0], "api_key")

    return templates.TemplateResponse("location_preference.html", {"lat":lat,"lng":lng,"preference":preference_value,"request": request})

@app.post("/set-location-preference")
async def update_location_preference(
    request: Request,
    preferences: int = Form(..., alias='preferences'),
):
    user_profile = UserProfile()

    # Fetch user id
    email = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    userId = cursor.fetchone()

    # Update the user's location preference in the database using edit_user_profile function
    location_preference_data = {
        'location_preference': preferences
    }

    user_profile.editUser(userId[0], location_preference_data)
    # Redirect to dashboard once preferences are submitted
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/set-age-preference")
async def set_age_preference(request: Request):
    # Visualize age preference picker (age_preference.html)
    return templates.TemplateResponse("age_preference.html", {"request": request})

@app.post("/set-age-preference")
async def update_age_preference(
    request: Request,
    min_age: int = Form(..., alias="minAge"),
    max_age: int = Form(..., alias="maxAge"),
):
    user_profile = UserProfile()

    # Fetch user id
    email = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    userId = cursor.fetchone()

    # Update the user's age preference in the database using the edit_user_profile function
    age_preference_data = {
        'min_age': min_age,
        'max_age': max_age
    }

    user_profile.editUser(userId[0], age_preference_data)
    # Redirect to dashboard once preferences are submitted
    return RedirectResponse(url="/dashboard", status_code=302)

@app.post("/upload-picture")
async def upload_picture(request: Request, picture: UploadFile = File(...)):
    # Ensure the upload directory exists
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    # Construct the file path
    file_path = os.path.join(UPLOAD_DIRECTORY, picture.filename)

    try:
        # Write the uploaded file to the specific path
        with open(file_path, "wb") as buffer:
            buffer.write(await picture.read())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    # Store data in dictionary
    userData = {
        'image_path': file_path
    }

    user_profile = UserProfile()

    # Fetch user id and edit the user information using the edit_user_profile function
    email = request.cookies.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    userId = cursor.fetchone()
    
    user_profile.editUser(userId[0],userData)

    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/chat/{email}")
async def chat(request: Request, email: str, response: Response):
    # Fetch user details and chat history based on `email`
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT firstName FROM users WHERE email = ?", (email,))
    name = cursor.fetchone()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    chatuserid = cursor.fetchone()

    # Set relevant cookies for chat feature
    response.set_cookie(key="chatid", value = chatuserid[0])
    response.set_cookie(key="name", value=name[0])
    user_email = request.cookies.get("email")
    cursor.execute("SELECT id FROM users WHERE email = ?", (user_email,))
    userId = cursor.fetchone()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    recipientId = cursor.fetchone()
    

    # Fetch chat history between logged-in user and the selected user
    cursor.execute("""
        SELECT u.firstName as sender_name, cm.message, cm.timestamp
        FROM userChat cm
        JOIN users u ON cm.sender_id = u.id
        WHERE (cm.sender_id = ? AND cm.receiver_id = ?) OR (cm.sender_id = ? AND cm.receiver_id = ?)
        ORDER BY cm.timestamp
    """, (userId[0], recipientId[0], recipientId[0], userId[0]))
    chat_history = cursor.fetchall()
    

    # Return the chat page with these details
    return templates.TemplateResponse("chat.html", {"name":name[0],"user_email":user_email,"chat_history": chat_history,"request": request})

@app.post("/send_message")
async def chat(request: Request, sender_id: str = Form(...), receiver_id: str = Form(...), message: str = Form(...)):

    # Fetch user details and chat history based on `email`
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE firstName = ?", (receiver_id,))
    receiver_id = cursor.fetchone()
    cursor.execute("SELECT email FROM users WHERE id = ?", (receiver_id[0],))
    email = cursor.fetchone()
    email = email[0]
    cursor.execute("SELECT id FROM users WHERE email = ?", (sender_id,))
    sender_id = cursor.fetchone()
    
    chatId = Identity.create_id()

    # Insert new chats into userChat table
    try:
        cursor.execute("""
            INSERT INTO userChat (id, sender_id, receiver_id, message, timestamp)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (chatId, sender_id[0], receiver_id[0], message))
        conn.commit()
        # Redirect you to chat page once new messages have been submitted
        return RedirectResponse(url=f"/chat/{email}?email={email}", status_code=302)
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
        


