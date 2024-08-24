# Tinder,But Better 
## (Please look at submission comments for API key (variable used in main.py and similarity_score.py))
This repository contains a Python-based matching application that calculates and displays user matches based on similarity scores. The app is modular, with separate files for data models, schemas, similarity score calculations, and user interactions.

## Project Structure
### Folders

- **`__pycache__/`**:
  - Contains cached bytecode files automatically generated by Python. These files help speed up the loading time of modules by avoiding recompilation.

- **`static/`**:
  - Stores static assets such as CSS, JavaScript, and image files used by the application, particularly for the web interface.

- **`templates/`**:
  - Holds HTML template files used to render dynamic web pages. These templates are filled with data and used to generate the HTML served to users.'

### Files
- **`data.py`**: 
  - Handles data-related operations, such as loading, processing, or interacting with the database. This file includes the initial data population for database tables.

- **`identity.py`**: 
  - Manages user identity and authentication processes. Recent updates added comments to improve code documentation.

- **`main.py`**: 
  - The main entry point of the application. Running this file initiates the application. Recent changes include adding a location filtering function.

- **`model.py`**: 
  - Defines the data models used throughout the application. These models represent the structure and relationships of the data. Recent updates added comments for clarity.

- **`schema.py`**: 
  - Defines the schema or blueprint of the data models, ensuring data integrity and consistency. A recent update added a foreign key constraint to one of the models.

- **`similarity_score.py`**: 
  - Contains the logic for calculating similarity scores between users or entities. These scores are used to determine the best matches. This file was recently updated as part of a merge process.

- **`user.py`**: 
  - Handles operations related to user management, such as creating and updating user profiles. The most recent update added comments for better understanding of the code.

- **`user_interaction.py`**: 
  - Manages interactions between the user and the application, including collecting user input and displaying results. The file was updated to include functionality for viewing matches.



## Features
### 1. User Profile Management

- **Profile Attributes:**
  - Each user profile contains the following attributes:
    - `user_id` (unique identifier)
    - `name`
    - `age`
    - `gender`
    - `location`
    - `interests` (list of interests)

- **Profile Actions:**
  - **Create a new user profile**
  - **View existing user profiles**
  - **Edit user profile details**
  - **Delete user profile**

### 2. User Interaction

- **Interaction Attributes:**
  - Tracks user interactions with the following attributes:
    - `liked_users` (list of user IDs that the user has liked)
    - `disliked_users` (list of user IDs that the user has disliked)
    - `matches` (list of user IDs that are mutual likes, based on a sophisticated matching algorithm)

- **Interaction Actions:**
  - **Like a user profile**
  - **Dislike a user profile**
  - **View matches** (based on user interactions, remembers likes and dislikes)

### 3. Data Storage and Management

- **Data Structures:**
  - Utilizes Python lists, tuples, and dictionaries to manage user profiles and interactions.

- **Database Integration:**
  - Implements a SQLite database to store user profiles and interactions.
  - Performs CRUD operations (Create, Read, Update, Delete) using SQL queries.
  - Uses the `sqlite3` library for database interactions.
 
### 4. Graphic User Interface (GUI)

- **User Commands:**
  - `create_user`: Create a new user profile
  - `view_profiles`: View all user profiles
  - `edit_profile`: Edit an existing user profile
  - `delete_profile`: Delete a user profile
  - `like_user`: Like a user profile
  - `dislike_user`: Dislike a user profile
  - `view_matches`: View matched user profiles

## Getting Started

### Prerequisites

This project requires Python 3.7 or higher and the following Python packages:

- PyCharm
- SQLite3
- NumPy
- Pandas
- Sentence Transformers
- Identity
- FastAPI
- Pydantic

### Installation

1. **Clone the repository: (PLEASE USE THE MASTER BRANCH) **

    ```bash
    git clone https://github.com/I-Am-Timothy-Williams/pythonmma2025.git
    cd pythonmma2025
    ```

2. **Create a virtual environment:**

    ```bash
    python3 -m venv venv
    ```

3. **Activate the virtual environment:**

    - On macOS/Linux:

        ```bash
        source venv/bin/activate
        ```

    - On Windows:

        ```bash
        venv\Scripts\activate
        ```

4. **Install the dependencies:**

    Make sure you have `pip` updated:

    ```bash
    pip install --upgrade pip
    ```

    Install the required packages using the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

### Dependencies

The following packages are required for this project:

- `numpy`
- `pandas`
- `sentence-transformers`
- `identity`
- `fastapi`
- `pydantic`

### Running the Application

After installation, you can start using the application with the following command:

```bash
fastapi dev tim_folder/main.py        
```


## Usage
1. **Input User Data:** Enter user data when prompted by the application.

<div align="center">
<img width="610" alt="Screenshot 2024-08-23 at 9 03 36 PM" src="https://github.com/user-attachments/assets/30a53196-4d4a-4958-a9bb-2ee7ede3c152">
</div>

**Login Page** prompts you to enter your email (emails are used for user identification if no username is set) and password to log in.

- For first-time users, please click **Register** at the bottom of the Login prompt to direct to the register page.
- For first-time logins, you’ll be prompted to select at least one of your **Interests** (out of a range of interest categories) to describe your hobbies and for matching people with similar interests.

2. **Registration**

To register, enter the following details:

<div align="center">
  <img width="615" alt="Screenshot 2024-08-23 at 9 08 13 PM" src="https://github.com/user-attachments/assets/514b59c9-2173-4c6b-b169-26d696b82036">
</div>


- **First Name**
- **Last Name**
- **Email** (used for identification if no username is set)
- **Age** (an integer)
- **Gender** (choose between "male"/"female")
- **Location** (address can be entered to improve matching accuracy, or you can enter general city/country for privacy purposes the program will pretty much accept anything as long as google maps can recognize the place)
- **Username** (required for login)
- **Password** (required for login)

Most importantly, please set up a username and password to log in and access the app.


3. **Dashboard**

The **Dashboard** allows you to view, edit, delete, and fill in more details for your profile.

<div align="center">
    <img width="491" alt="Screenshot 2024-08-23 at 9 11 20 PM" src="https://github.com/user-attachments/assets/07aa7d67-caaf-4f7d-8e9c-0d17843262e4">
</div>

- The top part of the **Dashboard** shows your profile information, including your name, email, location, age, and interests.
- You can use the buttons to:
  - **Edit Profile**
  - **Delete Profile**
  - **Set Age Range**
  - **Set Location Range**

### Editing Your Profile

If you click **Edit Profile**, a new prompt will appear, allowing you to update individual components that you entered during the registration stage. The **Interests** section can be edited into any free-typed interest for a better description of your interests. 

After making changes, click **Save Changes** to store your updates and return to the Dashboard.

<div align="center">
    <img width="489" alt="Screenshot 2024-08-23 at 9 12 17 PM" src="https://github.com/user-attachments/assets/612a3ea7-de04-47d2-941a-dbd7d8c0aa03">

</div>

You will also have the option to **upload a profile image**. You can save the image by clicking the submit button.

<div align="center">
    <img width="489" alt="Screenshot 2024-08-23 at 9 12 17 PM" src="https://i.imgur.com/u3riXTR.png">

</div>

### Delete Profile

The **Delete Profile** button will prompt you with a confirmation pop-up. If you agree to the prompt, your profile information will be permanently deleted from the database. You will then be immediately logged out and redirected to the login page.

### Age Range

The **Age Range** setting allows you to edit the minimum and maximum age of the people you want to see as profiles are pushed to you. This acts as a filter, ensuring that no profiles outside your selected age range will appear. Click **Save Preferences** to activate this filter, store your updates, and return to the Dashboard.

<div align="center">
    <img width="214" alt="Screenshot 2024-08-23 at 9 14 41 PM" src="https://github.com/user-attachments/assets/0a0fc3ae-f6c6-47c0-86cf-22aa6338a3c3">
</div>

### Location Range

The **Location Range** setting allows you to edit the maximum reach of the geographical location you want to see as profiles are pushed to you. Similar to the Age Range, this setting acts as a filter, ensuring no profiles outside your selected range will appear. Click **Update Radius** to visualize the range using our Google Maps plugin function. You can also enter specific addresses to visualize the radius/distances. Click **Save Preferences** to activate this filter, store your updates, and return to the Dashboard.

<div align="center">
    <img width="270" alt="Screenshot 2024-08-23 at 9 15 06 PM" src="https://github.com/user-attachments/assets/9aef6c44-2874-4e37-a0af-44dd43dd217d">

</div>

## PLEASE ENTER IN BOTH THE LOCATION AND AGE PREFERENCES TO GET STARTED WITH THE MATCHING PROCESS

### Dashboard - Profile Matching

The bottom section of the **Dashboard** displays profiles that are matched and pushed to you based on your personal data. The app calculates and identifies the best matches using a similarity score derived from your interests and those of other users.

- You can swipe the profile card left or right to indicate interest in the displayed profile and view the next one.
- There is a limit on how many profiles you can view based on your filters and the similarity of your interests.

<div align="center">
    <img width="487" alt="Screenshot 2024-08-23 at 9 16 22 PM" src="https://github.com/user-attachments/assets/72174679-47a6-4b24-8083-171995fdf76a">
</div>

### View Matches

The **View Matches** button allows you to see matched profiles that both you and the other user liked (both users need to click the heart icon or swipe right). Matches are displayed in order of relevance and the extent to which they match your interests.

<div align="center">
    <img width="1180" alt="Screenshot 2024-08-23 at 9 16 47 PM" src="https://github.com/user-attachments/assets/dd42004d-b44f-4588-ac56-064a374eb111">
</div>

### Chat with Matches

If you click on one of your matches, you will be able to open a chat with them and see your messages and their messages. Type out your sentiments in the input box and click **send** to update the chat with new messages.

<div align="center">
    <img width="1180" alt="Screenshot 2024-08-23 at 9 16 47 PM" src="https://i.imgur.com/f1UH9Ib.png">
</div>
