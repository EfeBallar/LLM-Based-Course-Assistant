"""THIS FUNCTION REMOVES A FILE FROM A COURSE"""
from vector_database import delete_chunks_from_file
from flask import request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()
DOC_PATH = os.getenv("DOC_PATH")
V_DB_PATH = os.getenv("V_DB_PATH")

def remove_helper(course_code, file_name):
    try:
       
        file_path = os.path.join(DOC_PATH, course_code, file_name)
        print(file_path)

        # If the path has more than one file, do not delete the folder
        has_multiple_files = len(os.listdir(os.path.join(DOC_PATH, course_code))) > 1

        if os.path.exists(file_path):
            try:
                os.remove(file_path)    # remove the file from documents folder
            except OSError as e:
                response_data = {
                    "status": 0,
                    "message": f"Error removing file: {str(e)}"
                }
                return response_data, 500

        else:
            response_data = {
                    "status": 0,
                    "message": "File path doesn't exist."
                }
            return response_data, 404
        
        # remove the file information from vector datavase
        delete_chunks_from_file(file_name, has_multiple_files, f"{V_DB_PATH}\\{course_code}_faiss_index.idx", f"{V_DB_PATH}\\{course_code}_metadata.pkl")

        response_data = {
            "status": 1,
            "message": f"{file_name} has been removed from {course_code}"
        }
        return response_data, 200

    except Exception as e:
        response_data = {
            "status": 0,
            "message": str(e)
        }
        return response_data, 500
    

def remove_files_from_course(course_db):
    try:
        # These will be obtained from raw JSON body
        course_code = request.json.get('course_code')
        files = request.json.get('data')

        if not files or not course_code:
            return jsonify({"error": "Course code and file names are required"}), 400

        if (not (isinstance(files, list) and all(isinstance(item, str) for item in files))):
            return jsonify({"error": "Invalid input, expected an array of strings"}), 400
            
        
        course = course_db.Courses.find_one({"courseCode": course_code})
        
        # if not course:
        #     return jsonify({"error": "Course not found"}), 404
       
        files_removed = []
        files_failed = []

        for file_name in files:
            response_data, http_code = remove_helper(course_code, file_name)
            
            if(response_data["status"] == 1):   # if the file has succesfully been added
                files_removed.append(file_name)
            else:
                files_failed.append(file_name)

        if (len(files) == len(files_removed)):    # if all the files are added successfully
            return jsonify({
                    "status": 1,
                    "message": "All files are removed"
                }), 200
        else:
            return jsonify({
                    "status": 0,
                    "message": f"Files [{', '.join(files_failed)}] are not removed."
                }), 409

    except Exception as e:
        return jsonify({
            "status": 0,
            "message": str(e)
        }), 500