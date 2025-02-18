"""THIS FUNCTION RETURNS THE FILES OF A COURSE"""
from flask import request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()
DOC_PATH = os.getenv("DOC_PATH")


def get_files_of_a_course(db):
    try:
        # Get the course code from the query parameters
        course_code = request.args.get('course_code')
        if not course_code:
            return jsonify({
                "status": 0,
                "files": None, 
                "file_count": None, 
                "msg": f"Course code is required."}), 400
            
        course = db.Courses.find_one({"courseCode": course_code})

        # if not course:
        #     return jsonify({"error": "Course not found"}), 404
        
        file_path = os.path.join(DOC_PATH, course_code)

        if not os.path.exists(file_path):
            return jsonify({
                "status": 0,
                "files": None, 
                "file_count": None, 
                "msg": f"There is no path created for {course_code} in the database."}), 404
        

        items = os.listdir(file_path)

    
        files = [
            {
                "name": item,
                "size": os.path.getsize(os.path.join(file_path, item))
            }
            for item in items if os.path.isfile(os.path.join(file_path, item))
        ]

        if len(files) == 0:
            return jsonify({
                "status": 1,
                "files": [], 
                "file_count": 0, 
                "msg": "There are no files for this course in the database."}), 404

        # Sort the files by filename
        files.sort(key=lambda x: x["name"])
        
        a = "is" if len(files) == 1 else "are"
        b = "file" if len(files) == 1 else "files"
        
        return jsonify({
            "status": 1,
            "files": files, 
            "file_count": len(files), 
            "msg": f"There {a} {len(files)} {b} for this course in the database."}), 200

    except Exception as e:
        return jsonify({
            "files": None,
            "file_count": None,
            "status": 0,
            "message": str(e)
        }), 500