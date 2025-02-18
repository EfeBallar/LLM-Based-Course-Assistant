import os
from flask import request, jsonify
from bson import ObjectId
from dotenv import load_dotenv
import shutil

load_dotenv()

# Local Related Variables
faiss_path = os.getenv("V_DB_PATH")
documents_path = os.getenv("DOC_PATH")

def delete_course(db):
    try:
        # Obtain parameters from the raw JSON body
        course_code = request.json.get('course_code')

        if not course_code:
            return jsonify({
                "status": "fail",
                "message": "Course code is required"
            }), 400

        # Find the course in the database
        course = db.Courses.find_one({"courseCode": course_code})
        if not course:
            return jsonify({
                "status": "fail",
                "message": f"Course with code {course_code} not found"
            }), 404

        # Iterate over personnel and remove the course code from their auth_courses
        for personnel_id in course["personnel_ids"]:
            db.Users.update_one(
                {"_id": ObjectId(personnel_id)},
                {"$pull": {"auth_courses": course_code}}  # Remove the course code from the array
            )

        # Delete the files in the documents folder related to the course
        documents_folder_path = os.path.join(documents_path, course_code)
        if os.path.exists(documents_folder_path):
            shutil.rmtree(documents_folder_path)  # Delete the entire folder and its content

         # Delete files in faiss folder that start with the course code
        faiss_folder_path = os.path.join(faiss_path, "faiss")  # Update with actual folder path
        if os.path.exists(faiss_folder_path):
            # Define the specific files to delete
            faiss_index_file = os.path.join(faiss_folder_path, f"{course_code}_faiss_index.idx")
            faiss_metadata_file = os.path.join(faiss_folder_path, f"{course_code}_metadata.pkl")
            
            # Remove the files if they exist
            if os.path.exists(faiss_index_file):
                os.remove(faiss_index_file)
            
            if os.path.exists(faiss_metadata_file):
                os.remove(faiss_metadata_file)

        # Delete the course from the Courses collection
        db.Courses.delete_one({"courseCode": course_code})

        # Return success message
        return jsonify({
            "status": "success",
            "message": f"Course {course_code} has been deleted and removed from all personnel's courses"
        }), 200

    except Exception as e:
        # Catch any unexpected errors
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
