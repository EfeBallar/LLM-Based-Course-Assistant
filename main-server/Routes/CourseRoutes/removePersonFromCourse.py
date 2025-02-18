"""THIS FUNCTION REMOVES A PERSON (INSTRUCTOR/ASSISTANT) FROM A COURSE"""
from flask import request, jsonify
from bson import ObjectId

def remove_person_from_course(db):
    try:
        # These will be obtained from raw JSON body
        user_name = request.json.get('user_name')
        course_code = request.json.get('course_code')

        if not user_name or not course_code:
            return jsonify({"error": "Username and course_code are required"}), 400
        
        user = db.Users.find_one({"email": f"{user_name}@sabanciuniv.edu"})
        if not user:
            return jsonify({"error": "User not found"}), 404
       
        course = db.Courses.find_one({"courseCode": course_code})
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        if (str(user["_id"]) in course["personnel_ids"]):

            # Remove the course code from user's auth_courses array
            db.Users.update_one(
                {"_id": ObjectId(user["_id"])},
                {"$pull": {"auth_courses": course_code}}
            )

            # Remove the user_id from the course's personnel array
            db.Courses.update_one(
                {"courseCode": course_code},
                {"$pull": {"personnel_ids": str(user["_id"])}}
            )

            return jsonify({
                "status": "success",
                "message": f"{user['name']} has been removed from {course_code}"
            }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500