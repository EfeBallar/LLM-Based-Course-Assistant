from flask import Flask, request, jsonify
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

# Load environment variables
load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# This function will create valid JWT tokens with the payload
def create_jwt_token(user_info):
    expiration_time = datetime.now(timezone.utc) + timedelta(days=1)  # Token expires in 1 day

    payload = {
        "email": user_info['email'],
        "given_name": user_info['given_name'],
        "family_name": user_info['family_name'],
        "google_id": user_info['google_id'],
        "mongo_id": user_info['mongo_id'],
        "role": user_info["role"],
        "exp": expiration_time
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token


def role_required(*allowed_roles):
    """Decorator for role-based access control."""
    from functools import wraps

    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization', None)
            if not auth_header:
                return jsonify({"status": 0, "message": "Token is missing!"}), 401

            try:
                token = auth_header.split(" ")[1].strip()
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
                user_role = payload.get("role", None)

                if user_role not in allowed_roles:
                    return jsonify({"status": 0, "message": "You do not have permission to access this resource."}), 403

                # Optionally attach user info to request context
                # request.user = payload

            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token has expired!", "status": 0}), 401
            except jwt.InvalidTokenError:
                return jsonify({"message": "Invalid token!", "status": 0}), 403

            return f(*args, **kwargs)
        return decorated
    return wrapper


def token_required(f):
    """Decorator to check and verify JWT token."""
    """This function will check the JWT token and handle permissions"""
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            token = auth_header.split(" ")[1].strip()  # Expecting 'Bearer <token>'
            
            # Verify JWT token
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            
            # Attach user info to request context
            request.user = {
                "email": payload["email"],
                "given_name": payload["given_name"],
                "family_name": payload["family_name"],
                "google_id": payload["google_id"]
            }

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!", "status": 0}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!", "status": 0}), 403

        return f(*args, **kwargs)

    return decorated


# this function will be used in the login route
def login(db):
    auth_header = request.headers.get('Authorization', None)
    if not auth_header:
        return jsonify({"message": "Token is missing!", "status": 0}), 401

    try:
        # Extract and verify the Google OAuth token
        token = auth_header.split(" ")[1].strip()
        id_info = id_token.verify_oauth2_token(
            token, google_requests.Request(), os.getenv("GOOGLE_CLIENT_ID")
        )


        # Create the JWT token after successful Google login
        user_info = {
            "email": id_info.get('email'),
            "given_name": id_info.get('given_name').replace(" (Student)", ""),
            "family_name": id_info.get('family_name').replace(" (Student)", ""),
            "google_id": id_info.get('sub').replace(" (Student)", ""),
        }

        user = db.Users.find_one({"email": user_info["email"]})
        
        # if there is no record of the user, meaning that they have not logged in before
        if not user:   
            # Insert new user document
            new_user = {
                "name": f"{user_info["given_name"]} {user_info["family_name"]}",    # full name of the user
                "email": user_info["email"],
                "role": "user",
                "auth_courses": []
            }
            user = db.Users.insert_one(new_user)
       

        user_info["mongo_id"] = str(user["_id"])
        user_info["role"] = user["role"]

        # Generate JWT token
        jwt_token = create_jwt_token(user_info)


        return jsonify({"message": "Login successful", "token": jwt_token, "status": 1}), 200

    except Exception as e:
        return jsonify({"message": "Invalid or expired token!", "error": str(e), "status": 0}), 403