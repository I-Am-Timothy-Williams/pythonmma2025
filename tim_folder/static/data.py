import sqlite3


conn = sqlite3.connect('tinder.db')
cursor = conn.cursor()

insert_users_data = """
INSERT INTO users (id, firstName, middleName, lastName, email, age, gender, location, interests, password) 
VALUES 
('1', 'John', 'A.', 'Doe', 'johndoe@example.com', 28, 'Male', 'Toronto', 'Hiking, Reading', 'password123'),
('2', 'Jane', 'B.', 'Smith', 'janesmith@example.com', 25, 'Female', 'Vancouver', 'Cooking, Traveling', 'securepassword456'),
('3', 'Michael', 'C.', 'Johnson', 'michaelj@example.com', 32, 'Male', 'Montreal', 'Photography, Music', 'mypassword789'),
('4', 'Emily', 'D.', 'Davis', 'emilydavis@example.com', 30, 'Female', 'Calgary', 'Yoga, Painting', 'emilypass123'),
('5', 'David', 'E.', 'Miller', 'davidmiller@example.com', 27, 'Male', 'Ottawa', 'Gaming, Biking', 'davidsafe456');
"""

cursor.execute(insert_users_data)

# Commit the transaction
conn.commit()

# Close the connection
conn.close()