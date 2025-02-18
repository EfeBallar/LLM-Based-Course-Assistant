from flask import Flask
from flask_cors import CORS
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

# Other Routes
from Routes.getCoursesOfALecturer import get_courses_of_a_lecturer
from Routes.query import query


app = Flask(__name__) #http://localhost:5000

db = connect_to_database()

# CORS Policy
CORS(app, origins=["http://localhost:3000"])

##################### GET Routes #####################
@app.route('/getUserID', methods=['GET'])
def get_user_id_route():
    return get_user_id(db)

@app.route('/getCourses', methods=['GET'])
def get_courses_route():
    return get_courses(db)

@app.route('/getPersonnelFromCourse', methods=['GET'])
def get_personnel_from_course_route():
    return get_personnel_from_course(db)

@app.route('/getUserChats', methods=['GET'])  
def get_user_chats_route():
    return get_user_chats(db)

@app.route('/getChatContent', methods=['GET'])  
def get_chat_content_route():
    return get_chat_content(db)

@app.route('/getLecturerCourses', methods=['GET'])  
def get_lecturer_courses_route():
    return get_courses_of_a_lecturer(db)

@app.route('/getCourseFiles', methods=['GET'])  
def get_course_files_route():
    return get_files_of_a_course(db)

##################### POST Routes #####################
@app.route('/', methods=['POST'])
def query_route():
    return query(db)

@app.route('/addCourse', methods=['POST'])
def add_course_route():
    return add_course(db)

##################### PUT Routes #####################
@app.route('/addPersonToCourse', methods=['PUT'])
def add_person_to_course_route():
    return add_person_to_course(db)

@app.route('/addFileToCourse', methods=['PUT'])
def add_file_to_course_route():
    return add_files_to_course(db) 

##################### DELETE Routes #####################
@app.route('/removeFileFromCourse', methods=['DELETE'])
def remove_file_from_course_route():
    return remove_files_from_course(db)

@app.route('/removePersonFromCourse', methods=['DELETE'])
def remove_person_from_course_route():
    return remove_person_from_course(db)

@app.route('/removeAllFilesFromCourse', methods=['DELETE'])
def remove_all_files_from_course_route():
    return remove_all_files_from_course(db) 

@app.route('/deleteCourse', methods=['DELETE'])
def delete_course_route():
    return delete_course(db) 

if __name__ == "__main__":
    app.run()