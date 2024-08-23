from identity import Identity
import sqlite3
import json

class UserProfile:
    @staticmethod
    def createUser(userData):
        # Generate a new unique ID for the user
        newUser = {
                'id': Identity.create_id(),
                'firstName': userData.get('firstName'),
                'middleName': userData.get('middleName'),
                'lastName': userData.get('lastName'),
                'email': userData.get('email'),
                'age': userData.get('age'),
                'gender': userData.get('gender'),
                'location': userData.get('location'),
                'interests': userData.get('interests'),
                'password': userData.get('password')
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

        # Inserts stored user data into users table
        cursor.execute('''
            INSERT INTO users (id, firstName, middleName, lastName, email, age, gender, location, interests, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            newUser['id'],
            newUser['firstName'],
            newUser['middleName'],
            newUser['lastName'],
            newUser['email'],
            newUser['age'],
            newUser['gender'],
            newUser['location'],
            interests_json,  # Store as a JSON string,
            newUser['password'],
        ))

        # Commit the transaction and close the database connection
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
            SELECT * FROM users WHERE id = ?
        ''', (userId,))

        user = cursor.fetchone() # Fetch the user's data

        conn.close() # Close the connection

        if user:
            # Convert the user information to a dictionary
            userInfo = {
                'userId': user['id'],
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

        # Convert any lists in updateData to JSON strings
        updateData = {key: json.dumps(value) if isinstance(value, list) else value for key, value in updateData.items()}

        # Prepare SQL query and parameters for updating user info. Set clause varies what sort of data we are trying to update based on the data we get
        set_clause = ', '.join(f"{key} = ?" for key in updateData.keys())
        sql_query = f'''
            UPDATE users
            SET {set_clause}
            WHERE id = ?
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
            DELETE FROM users WHERE id = ?
        ''', (userId,))

        # Check if any rows were affected
        if cursor.rowcount == 0:
            conn.close()
            return {'error': 'User not found'}

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

        return {'message': 'User deleted successfully'}
