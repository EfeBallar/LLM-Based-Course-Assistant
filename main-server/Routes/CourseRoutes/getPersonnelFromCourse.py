"""THIS FUNCTION GETS ALL PERSONS OF A COURSE"""
from flask import request, jsonify
from bson import ObjectId

def get_personnel_from_course(db):
    try:
        course_code = request.json.get('course_code')
        if not course_code:
            return jsonify({"error": "Course code is required"}), 400

        course = db.Courses.find_one({"courseCode": course_code})
        if not course:
            return jsonify({"error": "Course not found"}), 404
          
        personnel_ids = course['personnel_ids']
        personnel = list(db.Users.find({"_id": {"$in": [ObjectId(pid) for pid in personnel_ids]}}))
        personnel_names = [p['name'] for p in personnel]

        return jsonify({
            "personnel_ids": personnel_ids,
            "personnel_names": personnel_names
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500