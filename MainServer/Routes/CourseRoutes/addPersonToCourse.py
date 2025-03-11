"""THIS FUNCTION ADDS A PERSON (INSTRUCTOR/ASSISTANT) TO A COURSE"""
from flask import request, jsonify
from bson import ObjectId

def add_person_to_course(db):
    try:

        # These will be obtained from raw JSON body
        user_name = request.json.get('user_name')
        course_code = request.json.get('course_code')

        if not user_name or not course_code:
            return jsonify({"status": 0, "message": "Username and course_code are required"}), 401
        
        # Find the user by user_name
        user = db.Users.find_one({"email": f"{user_name}@sabanciuniv.edu"})
        if not user:
            return jsonify({"status": 0, "message": "User not found"}), 200
       
        course = db.Courses.find_one({"courseCode": course_code})
        if not course:
            return jsonify({"status": 0, "message": "Course not found"}), 200
        
        if (user["_id"] not in course["personnel_ids"]):    # if they are not already authorized
            
            # Add the course code to user's auth_courses array and set role to "Instructor"
            db.Users.update_one(
                {"_id": ObjectId(user["_id"])},
                {
                    "$addToSet": {"auth_courses": course_code},  # No duplicates allowed
                    "$set": {"role": "Instructor"}
                }
            )

            # Add the user_id to course's personnel array
            db.Courses.update_one(
                {"courseCode": course_code},
                {"$addToSet": {"personnel_ids": user["_id"]}} # No duplicates allowed
            )

            return jsonify({
                "status": 1,
                "message": f"{user['name']} has been added to {course_code}"
            }), 200

    except Exception as e:
        return jsonify({
            "status": 0,
            "message": str(e)
        }), 500