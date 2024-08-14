from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from user import UserProfile
import sqlite3
from pydantic import BaseModel
import hashlib
from urllib.parse import urlencode
from typing import List
import json



app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect('tinder.db')  # Update with your database file
    conn.row_factory = sqlite3.Row    
    return conn

def hash_password(password: str) -> str:
    # Hashing the password for comparison
    return hashlib.sha256(password.encode()).hexdigest()

def fetch_all_users(current_user_id, conn):
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

    user = user_profile.viewUser(userId[0])

    all_users = fetch_all_users(userId[0],get_db_connection())

    return templates.TemplateResponse("dashboard.html", {"request": request,"all_users":all_users, "user": user, "message": "User logged in successfully"})
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
