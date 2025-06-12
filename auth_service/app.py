from flask import Flask, request, jsonify
from pymongo import MongoClient
import jwt
import hashlib
import os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)

mongo_uri = os.environ.get('MONGO_URI', 'mongodb://admin:password123@localhost:27017/klea_ecommerce_auth?authSource=admin')
client = MongoClient(mongo_uri)
db = client.klea_ecommerce_auth
users_collection = db.users

JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    JWT_SECRET = 'klea_ecommerce_auth_secret_key'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "auth_service"}), 200

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not username or not password or not email:
            return jsonify({"error": "Username, password, and email are required"}), 400
        
        existing_user = users_collection.find_one({"$or": [{"username": username}, {"email": email}]})
        if existing_user:
            return jsonify({"error": "User already exists"}), 409
        
        hashed_password = hash_password(password)
        user_data = {
            "username": username,
            "password": hashed_password,
            "email": email,
            "created_at": datetime.utcnow()
        }
        
        result = users_collection.insert_one(user_data)
        
        return jsonify({
            "message": "User registered successfully",
            "user_id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        
        user = users_collection.find_one({"username": username})
        if not user or user['password'] != hash_password(password):
            return jsonify({"error": "Invalid credentials"}), 401
        
        payload = {
            "user_id": str(user['_id']),
            "username": username,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            "token": token,
            "user_id": str(user['_id']),
            "username": username
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/verify', methods=['POST'])
def verify_token():
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({"error": "Token is required"}), 400
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            return jsonify({
                "valid": True,
                "user_id": payload['user_id'],
                "username": payload['username']
            }), 200
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6001))
    app.run(host='0.0.0.0', port=port, debug=True) 