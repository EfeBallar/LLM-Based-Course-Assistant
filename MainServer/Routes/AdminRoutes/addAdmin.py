from flask import request, jsonify
from bson import ObjectId

def add_admin(db):
    try:
        # Obtain parameters from the raw JSON body
        instructor_id = request.json.get('instructor_id')

        # Validation for id field
        if not instructor_id:
            return jsonify({
                "status": 0,
                "message": "Instructor id is required"
            }), 400
        
        # Find the instructor by email
        instructor = db.Users.find_one({"_id": ObjectId(instructor_id)})
        if not instructor:
            return jsonify({
                "status": 0,
                "message": "Instructor not found"
            }), 404
        
        try:
            # Insert the user to Admins collection
            db.Admins.insert_one({
                "email": instructor["email"],
                "admin_id": ObjectId(instructor_id),
            })

        except Exception:
            # If user is already an admin, return a failure message
            return jsonify({
                "status": 0,
                "message": f"{instructor["name"]} is already an admin."
            }), 200

        # Update the role of the user
        db.Users.update_one(
            {"_id": ObjectId(instructor_id)},
            {"$set": {"role": "Admin"}}  
        )
        
        
        # Success response with a detailed message
        return jsonify({
            "status": 1,
            "message": f"{instructor["name"]} is now an Admin.",
        }), 200

    except Exception as e:
        # Catch any unexpected errors
        return jsonify({
            "status": 0,
            "message": str(e)
        }), 500
