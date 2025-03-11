from datetime import datetime, timedelta, timezone
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError


from flask import Flask, request, jsonify
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

from connectToDB import connect_to_database

# User Routes
from Routes.UserRoutes.getChatContent import get_chat_content
from Routes.UserRoutes.getUserChats import get_user_chats
from Routes.UserRoutes.getUserID import get_user_id

# Course Routes
from Routes.CourseRoutes.addCourse import add_course
from Routes.CourseRoutes.addPersonToCourse import add_person_to_course
from Routes.CourseRoutes.deleteCourse import delete_course
from Routes.CourseRoutes.getCourses import get_courses
from Routes.CourseRoutes.getPersonnelFromCourse import get_personnel_from_course
from Routes.CourseRoutes.removePersonFromCourse import remove_person_from_course

# File Routes
from Routes.FileRoutes.removeFileFromCourse import remove_files_from_course
from Routes.FileRoutes.addFileToCourse import add_files_to_course
from Routes.FileRoutes.removeAllFilesOfACourse import remove_all_files_from_course
from Routes.FileRoutes.getFilesOfACourse import get_files_of_a_course

# Admin Routes
from Routes.AdminRoutes.getAllAdmins import get_all_admins
from Routes.AdminRoutes.addAdmin import add_admin
from Routes.AdminRoutes.removeAdmin import remove_admin

# Other Routes
from Routes.getCoursesOfALecturer import get_courses_of_a_lecturer
from Routes.query import query
from Routes.loginRoute import login, role_required, token_required

# Load environment variables
load_dotenv()

# Create Database connection object

app = Flask(__name__) #http://localhost:5000
app.secret_key = os.getenv("SECRET_KEY")


# CORS Policy - Allow only frontend URL
CORS(app, origins=["http://localhost:3000"])

# Rate Limiting
# limiter = Limiter(
#     key_func=lambda: getattr(request, 'user', {}).get('email', get_remote_address()),
#     app=app,
#     default_limits=["200 per day", "50 per hour"]
# )

# Database connection
db = connect_to_database()
users_collection = db["Users"]  


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")






@app.route('/login', methods=['POST'])
def login_route():
    return login(db)



##################### GET Routes #####################
@app.route('/getUserID', methods=['GET'])
@token_required
def get_user_id_route():
    return get_user_id(db)

@app.route('/getCourses', methods=['GET'])
@token_required
def get_courses_route():
    return get_courses(db)

@app.route('/getPersonnelFromCourse', methods=['GET'])
@token_required
def get_personnel_from_course_route():
    return get_personnel_from_course(db)

@app.route('/getUserChats', methods=['GET'])  
@token_required
def get_user_chats_route():
    return get_user_chats(db)

@app.route('/getChatContent', methods=['GET'])  
@token_required
def get_chat_content_route():
    return get_chat_content(db)

@app.route('/getLecturerCourses', methods=['GET'])  
@token_required
def get_lecturer_courses_route():
    return get_courses_of_a_lecturer(db)

@app.route('/getCourseFiles', methods=['GET'])  
@token_required
def get_course_files_route():
    return get_files_of_a_course(db)

@app.route('/getAdmins', methods=['GET'])  
# @token_required
def get_admins_route():
    return get_all_admins(db)

##################### POST Routes #####################
@app.route('/', methods=['POST'])
# @token_required
def query_route():
    return query(db)

@app.route('/addCourse', methods=['POST'])
@token_required
def add_course_route():
    return add_course(db)

@app.route('/addAdmin', methods=['POST'])
# @token_required
def add_admin_route():
    return add_admin(db)

##################### PUT Routes #####################
@app.route('/addPersonToCourse', methods=['PUT'])
@token_required
def add_person_to_course_route():
    return add_person_to_course(db)

@app.route('/addFileToCourse', methods=['PUT'])
@token_required
def add_file_to_course_route():
    return add_files_to_course(db) 

##################### DELETE Routes #####################
@app.route('/removeFileFromCourse', methods=['DELETE'])
@token_required
def remove_file_from_course_route():
    return remove_files_from_course(db)

@app.route('/removePersonFromCourse', methods=['DELETE'])
@token_required
def remove_person_from_course_route():
    return remove_person_from_course(db)

@app.route('/removeAllFilesFromCourse', methods=['DELETE'])
@token_required
def remove_all_files_from_course_route():
    return remove_all_files_from_course(db) 

@app.route('/deleteCourse', methods=['DELETE'])
@token_required
def delete_course_route():
    return delete_course(db) 

@app.route('/removeAdmin', methods=['DELETE'])
# @token_required
def remove_admin_route():
    return remove_admin(db) 





# @app.route('/adminOnlyEndpoint', methods=['GET'])
# @role_required("Admin")
# def admin_only():
#     return jsonify({"message": "Welcome Admin! You have access to this route."})

# @app.route('/adminInstructorEndpoint', methods=['GET'])
# @role_required("Admin", "Instructor")
# def admin_instructor_only():
#     return jsonify({"message": "Hello Admin or Instructor! You can access this route."})

# @app.route('/authenticatedEndpoint', methods=['GET'])
# @token_required
# def authenticated_users():
#     return jsonify({"message": "Hello authenticated user! You can access this route."})


if __name__ == "__main__":
    app.run()