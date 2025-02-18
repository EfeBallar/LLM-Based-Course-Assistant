"""THIS FUNCTION RETURNS THE LIST OF COURSES OF A LECTURER"""
from flask import request, jsonify

def get_courses_of_a_lecturer(db):
    try:
        # These will be obtained from raw JSON body
        user_name = request.json.get('user_name')

        if not user_name:
            return jsonify({"error": "Username is required"}), 400
        
        # Find the user by user_name
        user = db.Users.find_one({"email": f"{user_name}@sabanciuniv.edu"})
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        else:

            return jsonify({
                "status": "success",
                "courses": user["auth_courses"]
            }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500