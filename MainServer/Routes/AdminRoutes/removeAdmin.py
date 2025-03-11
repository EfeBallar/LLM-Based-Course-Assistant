from bson import ObjectId
from flask import request
from pymongo import UpdateOne, DeleteOne

# Removes the admin with the matching id from Admins table, updates the Role information accordingly
def remove_admin(db):
    instructor_id = request.json.get('instructor_id')
    
    if not instructor_id:
        return {
            "status": 0,
            "message": "Instructor_id is required.",
        }, 400

    try:
        instructor_obj_id = ObjectId(instructor_id)

        # Call 1: Aggregate to get admin document + total count in Admins
        pipeline = [
            {"$match": {"_id": instructor_obj_id}},
            {"$lookup": {
                "from": "Admins",
                "pipeline": [{"$count": "admin_count"}],
                "as": "admin_count_docs"
            }}
        ]
        result = list(db.Users.aggregate(pipeline))
        if not result:
            return {
            "status": 0,
            "message": "Admin not found in Users table",
        }, 200

        admin_to_delete = result[0]

        admin_count = admin_to_delete.get("admin_count_docs", [{}])[0].get("admin_count", 0)

        if admin_count <= 1:
            return {"status":0, "message": "Cannot delete the only admin"}, 400

        # Prepare bulk operations (Call 2)
        courses_count = len(admin_to_delete.get("auth_courses", []))
        new_role = "Instructor" if courses_count > 0 else "User"

        operations = [
            UpdateOne({"_id": instructor_obj_id}, {"$set": {"role": new_role}}),
            DeleteOne({"admin_id": instructor_obj_id})
        ]

        db.Users.bulk_write([operations[0]])         # Update on Users
        db.Admins.bulk_write([operations[1]])        # Delete on Admins

        return {
            "status": 1,
            "message": f"{admin_to_delete["name"]}'s new role is {new_role}.",
        }, 200

    except Exception as e:
        return {"status": 0, "message": str(e)}, 500