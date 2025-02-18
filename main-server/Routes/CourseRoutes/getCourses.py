"""THIS FUNCTION GETS ALL COURSES IN THE MONGODB DATABASE"""
from flask import jsonify

def get_courses(db):
    try:
        courses = list(db.Courses.find({}))
        course_codes = [course["courseCode"] for course in courses]
        
        return jsonify({
            "courses": course_codes
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500