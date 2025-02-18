from connectToDB import connect_to_database
from pymongo import ASCENDING


db = connect_to_database()

# Create the Courses collection with a unique index on "courseCode"
db.Courses.create_index([("courseCode", ASCENDING)], unique=True)

# Create the Users collection with a unique index on "email"
db.Users.create_index([("email", ASCENDING)], unique=True)