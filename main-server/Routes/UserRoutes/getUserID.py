"""THIS FUNCTION RETURNS USER ID OF A USER"""
from flask import request, jsonify

def get_user_id(db):
    try:
        user_name = request.json.get('user_name')
        if not user_name:
            return jsonify({"error": "user_name is required"}), 400

        user = db.Users.find_one({"email": (user_name+"@sabanciuniv.edu")})
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user_id": str(user['_id'])
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500