from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)

mongo_uri = os.environ.get('MONGO_URI', 'mongodb://admin:password123@localhost:27017/klea_ecommerce_customer?authSource=admin')
client = MongoClient(mongo_uri)
db = client.klea_ecommerce_customer
customers_collection = db.customers

@app.route('/customers', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email', 'phone', 'address']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400
        
        customer_data = {
            "name": data['name'],
            "email": data['email'],
            "phone": data['phone'],
            "address": data['address'],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        existing_customer = customers_collection.find_one({"email": data['email']})
        if existing_customer:
            return jsonify({"error": "Customer with this email already exists"}), 409
        
        result = customers_collection.insert_one(customer_data)
        
        return jsonify({
            "message": "Customer created successfully",
            "customer_id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        if not ObjectId.is_valid(customer_id):
            return jsonify({"error": "Invalid customer ID"}), 400
            
        customer = customers_collection.find_one({"_id": ObjectId(customer_id)})
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        customer['_id'] = str(customer['_id'])
        return jsonify(customer), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/customers/<customer_id>/validate', methods=['GET'])
def validate_customer(customer_id):
    try:
        if not ObjectId.is_valid(customer_id):
            return jsonify({"valid": False, "error": "Invalid customer ID"}), 400
            
        customer = customers_collection.find_one({"_id": ObjectId(customer_id)})
        if not customer:
            return jsonify({"valid": False, "error": "Customer not found"}), 404
        
        return jsonify({
            "valid": True,
            "customer_id": str(customer['_id']),
            "name": customer['name'],
            "email": customer['email']
        }), 200
        
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

@app.route('/customers/<customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        if not ObjectId.is_valid(customer_id):
            return jsonify({"error": "Invalid customer ID"}), 400
            
        data = request.get_json()
        update_data = {}
        
        allowed_fields = ['name', 'email', 'phone', 'address']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400
        
        update_data['updated_at'] = datetime.utcnow()
        
        result = customers_collection.update_one(
            {"_id": ObjectId(customer_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Customer not found"}), 404
        
        return jsonify({"message": "Customer updated successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/customers', methods=['GET'])
def get_all_customers():
    try:
        customers = list(customers_collection.find())
        for customer in customers:
            customer['_id'] = str(customer['_id'])
        
        return jsonify(customers), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6002))
    app.run(host='0.0.0.0', port=port, debug=True) 