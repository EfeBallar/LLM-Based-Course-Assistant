"""THIS FUNCTION GETS ALL CHATS FOR A USER"""
from flask import request, jsonify
from bson import ObjectId
from datetime import datetime

# Helper Function to Get Relevant Data
def extract_fields(data):
    result = []
    for entry in data:
        try:
            result.append({
                "course": entry["course"],
                "_id": entry["_id"],
                "title": entry["title"],
                "last_message_time": entry["last_message_time"]
            })
        except Exception as e:
            print(f"Error processing entry {entry}: {e}")
    return result


def get_user_chats(db):
    try:
        user_name = request.args.get('user_name')  # Get 'user_name' from query parameters
        
        if not user_name:
            return jsonify({"error": "Username is required"}), 400
        
        user = db.Users.find_one({"_id": ObjectId(user_name)})
        # user = db.Users.find_one({"email": f"{user_name}@sabanciuniv.edu"})
        if not user:
            return jsonify({"error": "User not found"}), 404
        try:
            # Find all chats where the user is a participant
            chats = list(db.Chats.find({"user_id": str(user["_id"])}))
        except:
            return jsonify({
                "error": "Chats collection cannot be found."
            }), 409
            
        chats = extract_fields(chats)



        # Convert ObjectId to string and prepare chats for JSON serialization
        for chat in chats:
            chat['_id'] = str(chat['_id'])
        
    
        # Create a sorted list of chat IDs with their last message times
        chats.sort(key=lambda x: x['last_message_time'], reverse=True)

        
        return jsonify({
            "chats": chats
        }), 200
        

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500