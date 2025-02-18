from flask import request, jsonify
from bson import ObjectId

def add_course(db):
    try:
        # Obtain parameters from the raw JSON body
        instructor_username = request.json.get('instructor_username')
        course_code = request.json.get('course_code')
        course_name = request.json.get('course_name')

        # Validation for required fields
        if not instructor_username or not course_code or not course_name:
            return jsonify({
                "status": "fail",
                "message": "Instructor username and course code/name are required"
            }), 400
        
        # Find the instructor by email
        instructor = db.Users.find_one({"email": f"{instructor_username}@sabanciuniv.edu"})
        if not instructor:
            return jsonify({
                "status": "fail",
                "message": "Instructor not found"
            }), 404
        
        try:
            # Insert the course into the Courses collection
            db.Courses.insert_one({
                "courseName": course_name,
                "courseCode": course_code,
                "personnel_ids": [instructor["_id"]]
            })
        except Exception:
            # If course already exists, return a failure message
            return jsonify({
                "status": "fail",
                "message": f"{course_code} already exists."
            }), 200

        # Add the course to the instructor's authorized courses list
        db.Users.update_one(
            {"_id": ObjectId(instructor["_id"])},
            {"$addToSet": {"auth_courses": course_code}}  # Avoid duplicates
        )

        # Success response with a detailed message
        return jsonify({
            "status": "success",
            "message": f"{course_code} has been created and added to {instructor['name']}'s courses",
            "data": {
                "courseCode": course_code,
                "courseName": course_name,
                "instructor": instructor["name"]
            }
        }), 200

    except Exception as e:
        # Catch any unexpected errors
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
