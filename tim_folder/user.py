from identity import Identity
import sqlite3
import json

class UserProfile:
    @staticmethod
    def createUser(userData):
        newUser = {
                'userId': Identity.create_id(),
                'firstName': userData.get('firstName'),
                'middleName': userData.get('middleName'),
                'lastName': userData.get('lastName'),
                'email': userData.get('email'),
                'age': userData.get('age'),
                'gender': userData.get('gender'),
                'location': userData.get('location'),
                'interests': userData.get('interests')
        }
        # Save the user profile to the SQLite database
        conn = sqlite3.connect('tinder.db')
        cursor = conn.cursor()

         # Check if the email already exists
        cursor.execute('''
            SELECT * FROM users WHERE email = ?
        ''', (userData.get('email'),))

        existing_user = cursor.fetchone()

        if existing_user:
            # Close the connection and return an error if the email is found
            conn.close()
            return {'error': 'An account with this email already exists.'}

        # Convert interests list to a JSON string
        interests_json = json.dumps(newUser['interests'])

        cursor.execute('''
            INSERT INTO users (userId, firstName, middleName, lastName, email, age, gender, location, interests)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            newUser['userId'],
            newUser['firstName'],
            newUser['middleName'],
            newUser['lastName'],
            newUser['email'],
            newUser['age'],
            newUser['gender'],
            newUser['location'],
            interests_json  # Store as a JSON string
        ))

        conn.commit()
        conn.close()

        return
    
    @staticmethod
    def viewUser(userId):
        # Connect to the database
        conn = sqlite3.connect('tinder.db')
        conn.row_factory = sqlite3.Row  # Use Row factory to access columns by name
        cursor = conn.cursor()

        # Query to retrieve user information based on userId
        cursor.execute('''
            SELECT * FROM users WHERE userId = ?
        ''', (userId,))

        user = cursor.fetchone()

        conn.close()

        if user:
            # Convert the user information to a dictionary
            userInfo = {
                'userId': user['userId'],
                'firstName': user['firstName'],
                'middleName': user['middleName'],
                'lastName': user['lastName'],
                'email': user['email'],
                'age': user['age'],
                'gender': user['gender'],
                'location': user['location'],
                'interests': json.loads(user['interests'])  # Convert JSON string back to list
            }
            return userInfo
        else:
            return {'error': 'User not found'}
    @staticmethod
    def editUser(userId, updateData):
        # Connect to the database
        conn = sqlite3.connect('tinder.db')
        cursor = conn.cursor()

        # Prepare SQL query and parameters for updating user info
        set_clause = ', '.join(f"{key} = ?" for key in updateData.keys())
        sql_query = f'''
            UPDATE users
            SET {set_clause}
            WHERE userId = ?
        '''

        # Execute the update query
        cursor.execute(sql_query, (*updateData.values(), userId))

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

        return {'message': 'User information updated successfully'}
    @staticmethod
    def deleteUser(userId):
        # Connect to the database
        conn = sqlite3.connect('tinder.db')
        cursor = conn.cursor()

        # Execute DELETE query
        cursor.execute('''
            DELETE FROM users WHERE userId = ?
        ''', (userId,))

        # Check if any rows were affected
        if cursor.rowcount == 0:
            conn.close()
            return {'error': 'User not found'}

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

        return {'message': 'User deleted successfully'}



#need to fetch userData from GUI
userData = {
    'firstName': 'Jane',
    'middleName': 'Q',
    'lastName': 'Doe',
    'email': 'jane.doe@example.com',
    'age': 28,
    'gender': 'female',
    'location': 'New York',
    'interests': ['reading', 'traveling']
}


user_profile = UserProfile.createUser(userData)
print(user_profile)
user_info = UserProfile.viewUser('8b95686f518e4b458d4f6952c433434c')
print(user_info)
updateData = {
    'firstName': 'Janecia',
    'location': 'Los Angeles',
    'email': 'janetjackson@gmail.com',
    'interests': json.dumps(['hiking', 'photography'])  # Convert list to JSON string
}

# Attempt to update the user profile
result = UserProfile.editUser('8b95686f518e4b458d4f6952c433434c', updateData)
result = UserProfile.deleteUser('2da3f4f20daa4440a84bda8448b883b6')
print(result)  # Print the result message