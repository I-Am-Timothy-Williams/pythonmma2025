import sqlite3
from identity import Identity
from user import UserProfile
class UserInteraction:
    @staticmethod
    def likeUser(userId,likeduserId):
        # Connect to the database
        conn = sqlite3.connect('tinder.db')
        cursor = conn.cursor()

        # Generate a unique ID for the like
        likeId = Identity.create_id()

        # Insert the like information into the userLikes table
        cursor.execute('''
            INSERT INTO userLikes (id, userId, userLikes, dateCreated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            likeId,       # Generated unique ID
            userId,       # The ID of the user who is liking someone
            likeduserId   # The ID of the user who is being liked
        ))

        # Commit the transaction and close the connection
        conn.commit()
        match = UserInteraction.checkMatches(userId, likeduserId, cursor)
        conn.close()

        if match:
            return {'message': 'It\'s a match!'}
        else:
            return {'message': 'User liked successfully'}
    @staticmethod
    def checkMatches(userId, likedUserId, cursor):
        # Check if likedUserId has already liked userId
        cursor.execute('''
            SELECT * FROM userLikes
            WHERE userId = ? AND userLikes = ?
        ''', (likedUserId, userId))
        
        result = cursor.fetchone()
        
        # If there's a result, it's a match
        if result:
         # Insert the match into userMatches table
            matchId = Identity.create_id()
            try:
                cursor.execute('''
                    INSERT INTO userMatches (id, user1Id, user2Id, isMatch, dateCreated)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    matchId,       # Generated unique ID for the match
                    userId,        # The ID of the first user
                    likedUserId,   # The ID of the second user
                    1              # Indicating it's a match (could be a boolean)
                ))

                # Commit the match insertion
                cursor.connection.commit()
            except sqlite3.IntegrityError as e:
                return {'error': str(e)}
            return True
        return False
    @staticmethod
    def dislikeUser(userId,dislikeduserId):
        # Connect to the database
        conn = sqlite3.connect('tinder.db')
        cursor = conn.cursor()

        # Generate a unique ID for the like
        likeId = Identity.create_id()

        # Insert the like information into the userLikes table
        cursor.execute('''
            INSERT INTO userDislikes (id, userId, userDislikes, dateCreated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            likeId,       # Generated unique ID
            userId,       # The ID of the user who is disliking someone
            dislikeduserId   # The ID of the user who is being disliked
        ))

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

        return {'message': 'User disliked successfully'}
    @staticmethod
    def viewMatches(userId):
        # Connect to the database
        conn = sqlite3.connect('tinder.db')
        cursor = conn.cursor()

        # provide details of both persons that are matched
        cursor.execute('''
                SELECT 
                    u1.id, u1.firstName, u1.lastName, u1.age, u1.gender,u1.location,u1.interests
                    u2.id, u2.firstName, u2.lastName, u2.age, u2.gender,u2.location,u2.interests
                FROM userMatches
                JOIN users u1 ON userMatches.user1Id = u1.id
                JOIN users u2 ON userMatches.user2Id = u2.id
                WHERE (user1Id = ? OR user2Id = ?) AND isMatch = 1;
            ''', (userId,userId))

        # Fetch all matching rows
        matches = cursor.fetchall()

        # Print the matches
        print(f"Confirmed matches for user ID {userId}:")
        for match in matches:
            # Check if userId is user1 or user2 and print the other user's information
            if match[0] == userId:  # Alice is user1
                print(
                    f"Matched with: {match[8]} {match[9]} - Age: {match[10]}, Gender: {match[11]}, Location: {match[12]}, Interests: {match[13]}")
            else:  # Alice is user2
                print(
                    f"Matched with: {match[1]} {match[2]} - Age: {match[3]}, Gender: {match[4]}, Location: {match[5]}, Interests: {match[6]}")

        # Close the connection
        conn.close()

# Example usage
userId = '2c39c4521cd84465ae2c0bcc37efbe5a'  # Replace with the actual user ID
likedUserId = '6bb138eebc284c989760eaf6cc4c4574'  # Replace with the ID of the liked user

result = UserInteraction.likeUser(likedUserId, userId)
# result = UserInteraction.dislikeUser(dislikedUserId,userId)
print(result)  # Should print: {'message': 'User liked successfully'}
