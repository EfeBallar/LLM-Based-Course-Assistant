from vector_database import save_chunks_to_faiss,embed_chunks,generate_chunks_from_file
from flask import request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()
DOC_PATH = os.getenv("DOC_PATH")
V_DB_PATH = os.getenv("V_DB_PATH")

"""THIS FUNCTION ADDS A FILE TO A COURSE"""
"""It will act as a helper function to add multiple files to the course"""
def add_helper(file_to_add, course_code):
                      
    try:
        file_path = os.path.join(DOC_PATH + "\\" + course_code)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        doc_path=os.path.join(file_path, file_to_add.filename)
        
        if os.path.isfile(doc_path):
            response_data = {
                "status": 0,  
                "message": f"{file_to_add.filename} already exists"
            }
            return response_data, 409
        
        file_to_add.save(doc_path) # Save with the full path in documents folder
        

        chunks_data = generate_chunks_from_file(doc_path, 1000, 200)
        for chunk in chunks_data:
            chunk["file"] = file_to_add.filename
            
        new_chunks_data = embed_chunks(chunks_data, "all-MiniLM-L6-v2", True)
        try:
            save_chunks_to_faiss(new_chunks_data, f"{V_DB_PATH}\\{course_code}_faiss_index.idx", f"{V_DB_PATH}\\{course_code}_metadata.pkl")
            response_data = {
                "status": 1, 
                "message": "File has been saved"
            }
            return response_data, 200
        except Exception as e:
            print(e)        

    except:
        response_data = {
                "status": 0, 
                "message": "File could not be saved"
            }
        return response_data, 400
        
    return jsonify({
        "status": 1,
        "message": f"{file_to_add.filename} has been added to {course_code}"
    }), 200

   

""""This function can add multiple files to a course"""
""""saving the original file in the cours folder and"""
"""saving the content in FAISS vector database"""
def add_files_to_course(db):
    course_code = request.form.get('course_code')  
    files = request.files.getlist('files')
    
        
    if not course_code or not files:
        return jsonify({
                "status": 0,
                "message": "Files and course_code are required"
            }), 400

    course = db.Courses.find_one({"courseCode": course_code})
        
    # if not course:
    #     return jsonify({"error": "Course not found"}), 404
    
    files_added = []    # this will keep track of files that are successfully added
    files_failed = []   # this will keep track of files that are not added due to error
    for file in files:
        response_data, http_code = add_helper(file, course_code) 
        if(response_data["status"] == 1):   # if the file has succesfully been added
            files_added.append(file.filename)
        else:
            files_failed.append(file.filename)
    
    if (len(files) == len(files_added)):    # if all the files are added successfully
        return jsonify({
                "status": 1,
                "message": "All files are saved successfully"
            }), 200
    else:
        return jsonify({
                "status": 0,
                "message": f"Files [{', '.join(files_failed)}] are not saved."
            }), 409
