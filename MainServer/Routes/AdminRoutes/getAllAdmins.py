from flask import request, jsonify

"""THIS FUNCTION GETS ALL ADMINS IN THE MONGODB DATABASE"""
def get_all_admins(db):
    try:
        admins = list(db.Admins.find({}))

        admins = [{
            "_id": str(admin["_id"]),
            "admin_id": str(admin["admin_id"]),
            "email": admin["email"],
            } 
        for admin in admins]
        
        return jsonify({
            "status": 1,
            "admins": admins
        }), 200

    except Exception as e:
        return jsonify({
            "status": 0,
            "message": str(e)
        }), 500
    