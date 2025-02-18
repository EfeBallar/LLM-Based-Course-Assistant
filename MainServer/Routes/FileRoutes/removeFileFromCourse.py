"""THIS FUNCTION REMOVES A FILE FROM A COURSE"""
from vector_database import delete_chunks_from_file
from flask import request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()
DOC_PATH = os.getenv("DOC_PATH")
V_DB_PATH = os.getenv("V_DB_PATH")

def remove_file_from_course(course_db):
    try:
        # These will be obtained from raw JSON body
        file_name = request.args.get('file_name')
        course_code = request.args.get('course_code')


        if not file_name or not course_code:
            return jsonify({"error": "Course code and file name are required"}), 400
        
        course = course_db.Courses.find_one({"courseCode": course_code})
        
        # if not course:
        #     return jsonify({"error": "Course not found"}), 404
       
        file_path = os.path.join(DOC_PATH, course_code, file_name)
        print(file_path)

        # If the path has more than one file, do not delete the folder
        has_multiple_files = len(os.listdir(os.path.join(DOC_PATH, course_code))) > 1

        if os.path.exists(file_path):
            try:
                os.remove(file_path)    # remove the file from documents folder
            except OSError as e:
                return jsonify({"error": f"Error removing file: {str(e)}"}), 500

        else:
            return jsonify({"error": "File path doesn't exist."}), 404
        
        # remove the file information from vector datavase
        delete_chunks_from_file(file_name, has_multiple_files, f"{V_DB_PATH}\\{course_code}_faiss_index.idx", f"{V_DB_PATH}\\{course_code}_metadata.pkl")

        return jsonify({
            "status": 1,
            "message": f"{file_name} has been removed from {course_code}"
        }), 200

    except Exception as e:
        return jsonify({
            "status": 0,
            "message": str(e)
        }), 500