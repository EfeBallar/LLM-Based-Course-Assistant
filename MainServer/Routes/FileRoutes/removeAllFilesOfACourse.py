"""THIS FUNCTION REMOVES ALL FILES OF A COURSE"""
from flask import request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()
DOC_PATH = os.getenv("DOC_PATH")
V_DB_PATH = os.getenv("V_DB_PATH")

def remove_all_files_from_course(course_db):
    try:
        # These will be obtained from raw JSON body
        course_code = request.args.get('course_code')

        if not course_code:
            return jsonify({"error": "Course code is required"}), 400
        
        course = course_db.Courses.find_one({"courseCode": course_code})
        
        # if not course:
        #     return jsonify({"error": "Course not found"}), 404
       
        course_data_path = os.path.join(DOC_PATH, course_code)
        print(f"course_data_path: {course_data_path}")

        if os.path.exists(course_data_path):
            try:
                for file in os.listdir(course_data_path):
                    os.remove(os.path.join(course_data_path, file))

            except OSError as e:
                return jsonify({"error": f"Error removing file: {str(e)}"}), 500

        else:
            return jsonify({"error": "Course path in data doesn't exist."}), 404

        # faiss_data_path = V_DB_PATH
        # print(f"faiss_data_path: {V_DB_PATH}")
        # if os.path.exists(V_DB_PATH):
        #     try:
        #         for file in os.listdir(V_DB_PATH):
        #             os.remove(os.path.join(V_DB_PATH, file))

        #     except OSError as e:
        #         return jsonify({"error": f"Error removing file: {str(e)}"}), 500
        if os.path.exists(V_DB_PATH):
            try:
                index_file = os.path.join(V_DB_PATH, f"{course_code}_faiss_index.idx")
                metadata_file = os.path.join(V_DB_PATH, f"{course_code}_metadata.pkl")

                print(f"index_file: {index_file}")
                print(f"metadata_file: {metadata_file}")

                # Remove files only if they exist
                if os.path.exists(index_file):
                    os.remove(index_file)
                if os.path.exists(metadata_file):
                    os.remove(metadata_file)

            except OSError as e:
                return jsonify({"error": f"Error removing file: {str(e)}"}), 500

        else:
            return jsonify({"error": "Course path in chroma doesn't exist."}), 404

        return jsonify({
            "status": 1,
            "message": f"All files has been removed from {course_code}"
        }), 200

    except Exception as e:
        return jsonify({
            "status": 0,
            "message": str(e)
        }), 500