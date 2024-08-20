import sqlite3
from identity import Identity
from user import UserProfile
class UserInteraction:
    @staticmethod
    def likeUser(userId,likedUserId):
        # Connect to the database
        conn = sqlite3.connect('tinder.db')
        cursor = conn.cursor()

        # Generate a unique ID for the like
        likeId = Identity.create_id()

        cursor.execute('''
        SELECT * FROM userLikes WHERE userId = ? AND userLikes = ?
''',(userId,likedUserId))
        user = cursor.fetchone()
        if user:
            print('hi im user', userId,likedUserId)
            return {'message': 'User already liked'}
        print('hi')
        # Insert the like information into the userLikes table
        cursor.execute('''
            INSERT INTO userLikes (id, userId, userLikes, dateCreated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            likeId,       # Generated unique ID
            userId,       # The ID of the user who is liking someone
            likedUserId   # The ID of the user who is being liked
        ))

        # Commit the transaction and close the connection
        conn.commit()
        print('hi im user', userId,likedUserId  )
        match = UserInteraction.checkMatches(userId, likedUserId, cursor)
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
        return


# Example usage
userId = '2c39c4521cd84465ae2c0bcc37efbe5a'  # Replace with the actual user ID
likedUserId = '6bb138eebc284c989760eaf6cc4c4574'  # Replace with the ID of the liked user

result = UserInteraction.likeUser(likedUserId, userId)
# result = UserInteraction.dislikeUser(dislikedUserId,userId)
print(result)  # Should print: {'message': 'User liked successfully'}