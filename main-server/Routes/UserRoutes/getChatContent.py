"""THIS FUNCTION GETS CONTENTS OF A SPECIFIC CHAT OF A USER USING THE CHAT ID"""
from flask import request, jsonify
from bson import ObjectId


def get_chat_content(db):
    try:
        chat_id = request.args.get('chat_id')  # Get 'chat_id' from query parameters

        if not chat_id:
            return jsonify({"error": "Chat ID is required"}), 400

        chat = db.Chats.find_one({"_id": ObjectId(chat_id)})

        if not chat:
            return jsonify({"error": "chat not found"}), 404

        
        return jsonify({
            "chat": 
            {
                '_id': str(chat["_id"]),
                'user_id': chat["user_id"],
                'started_at': chat["started_at"],
                'last_message_time': chat["last_message_time"],
                'messages': chat["messages"],
                'title': chat["title"],
                'course': chat["course"],
            }
        }), 200
        

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500