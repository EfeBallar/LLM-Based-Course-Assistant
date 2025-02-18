"""THIS FUNCTION GETS ALL PERSONS OF A COURSE"""
from flask import request, jsonify
from bson import ObjectId

def get_personnel_from_course(db):
    try:
        course_code = request.args.get('course_code')
        if not course_code:
            return jsonify({"error": "Course code is required"}), 400

        course = db.Courses.find_one({"courseCode": course_code})
        if not course:
            return jsonify({"error": "Course not found"}), 404
          
        personnel_ids = [str(id) for id in course['personnel_ids']]

        personnel = list(db.Users.find({"_id": {"$in": [ObjectId(pid) for pid in personnel_ids]}}))
        personnel_data = [{"id": str(p['_id']), "name": p['name']} for p in personnel]

        return jsonify({
            "personnel_data": personnel_data
        }), 200

    except Exception as e:
        return jsonify({
            "status": 0,
            "message": str(e)
        }), 500