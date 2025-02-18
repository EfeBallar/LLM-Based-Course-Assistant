"""THIS FUNCTION ADDS A FILE TO A COURSE"""
from vector_database import add_chunks_to_faiss,embed_chunks,generate_chunks_from_file
from flask import request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()
DOC_PATH = os.getenv("DOC_PATH")
V_DB_PATH = os.getenv("V_DB_PATH")

def add_file_to_course(course_db):
    try:
        # get the PDF file here and put it to fileToAdd variable, key = fileName
        # get the course code here and put it to courseCode variable, key = courseCode 
        file_to_add = request.files.get('file')
        course_code = request.form.get('courseCode')  
        
       
        if not course_code or not file_to_add:
            return jsonify({"error": "File and course_code are required"}), 400
        
        course = course_db.Courses.find_one({"courseCode": course_code})
        
        # if not course:
        #     return jsonify({"error": "Course not found"}), 404
        
        try:
            file_path = os.path.join(DOC_PATH + "\\" + course_code)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            doc_path=os.path.join(file_path, file_to_add.filename)
            
            if os.path.isfile(doc_path):
                return jsonify({"error": f"{file_to_add.filename} already exists"}), 409
            
            file_to_add.save(doc_path) # Save with the full path
            

            chunks_data = generate_chunks_from_file(doc_path, 1000, 200)

            for chunk in chunks_data:
                chunk["pdf"] = file_to_add.filename
                
            new_chunks_data = embed_chunks(chunks_data, "all-MiniLM-L6-v2", True)
            add_chunks_to_faiss(new_chunks_data, course_code+"_faiss_index.idx", course_code+"_metadata.pkl")
            

        except:
            return jsonify({"error": "File could not be saved"}), 400
            
        return jsonify({
            "status": "success",
            "message": f"{file_to_add.filename} has been added to {course_code}"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500