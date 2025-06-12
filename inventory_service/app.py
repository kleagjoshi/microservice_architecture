from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)

mongo_uri = os.environ.get('MONGO_URI', 'mongodb://admin:password123@localhost:27017/klea_ecommerce_inventory?authSource=admin')
client = MongoClient(mongo_uri)
db = client.klea_ecommerce_inventory
products_collection = db.products
reservations_collection = db.reservations


@app.route('/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        
        required_fields = ['name', 'price', 'stock_quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400
        
        product_data = {
            "name": data['name'],
            "description": data.get('description', ''),
            "price": float(data['price']),
            "stock_quantity": int(data['stock_quantity']),
            "reserved_quantity": 0,
            "available_quantity": int(data['stock_quantity']),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = products_collection.insert_one(product_data)
        
        return jsonify({
            "message": "Product created successfully",
            "product_id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/products', methods=['GET'])
def get_products():
    try:
        products = list(products_collection.find())
        for product in products:
            product['_id'] = str(product['_id'])
        
        return jsonify(products), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        if not ObjectId.is_valid(product_id):
            return jsonify({"error": "Invalid product ID"}), 400
            
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        product['_id'] = str(product['_id'])
        return jsonify(product), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/products/<product_id>/availability', methods=['GET'])
def check_availability(product_id):
    try:
        if not ObjectId.is_valid(product_id):
            return jsonify({"available": False, "error": "Invalid product ID"}), 400
            
        quantity = int(request.args.get('quantity', 1))
        
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return jsonify({"available": False, "error": "Product not found"}), 404
        
        available = product['available_quantity'] >= quantity
        
        return jsonify({
            "available": available,
            "product_id": str(product['_id']),
            "requested_quantity": quantity,
            "available_quantity": product['available_quantity'],
            "stock_quantity": product['stock_quantity'],
            "reserved_quantity": product['reserved_quantity']
        }), 200
        
    except Exception as e:
        return jsonify({"available": False, "error": str(e)}), 500

@app.route('/products/<product_id>/reserve', methods=['POST'])
def reserve_product(product_id):
    try:
        if not ObjectId.is_valid(product_id):
            return jsonify({"reserved": False, "error": "Invalid product ID"}), 400
            
        data = request.get_json()
        quantity = int(data.get('quantity', 1))
        customer_id = data.get('customer_id')
        
        if not customer_id:
            return jsonify({"reserved": False, "error": "customer_id is required"}), 400
        
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return jsonify({"reserved": False, "error": "Product not found"}), 404
        
        if product['available_quantity'] < quantity:
            return jsonify({
                "reserved": False,
                "error": "Insufficient stock",
                "available_quantity": product['available_quantity'],
                "requested_quantity": quantity
            }), 400
        
        # Create reservation record
        reservation_data = {
            "product_id": ObjectId(product_id),
            "customer_id": customer_id,
            "quantity": quantity,
            "status": "reserved",
            "created_at": datetime.utcnow(),
            "reserved_at": datetime.utcnow()
        }
        
        result = reservations_collection.insert_one(reservation_data)
        
        # Update product quantities
        products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {
                "$inc": {
                    "reserved_quantity": quantity,
                    "available_quantity": -quantity
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return jsonify({
            "reserved": True,
            "reservation_id": str(result.inserted_id),
            "product_id": product_id,
            "quantity": quantity,
            "customer_id": customer_id
        }), 200
        
    except Exception as e:
        return jsonify({"reserved": False, "error": str(e)}), 500

@app.route('/reservations/<reservation_id>/confirm', methods=['POST'])
def confirm_reservation(reservation_id):
    try:
        if not ObjectId.is_valid(reservation_id):
            return jsonify({"confirmed": False, "error": "Invalid reservation ID"}), 400

        reservation = reservations_collection.find_one({"_id": ObjectId(reservation_id)})
        if not reservation:
            return jsonify({"confirmed": False, "error": "Reservation not found"}), 404
        
        if reservation['status'] != 'reserved':
            return jsonify({"confirmed": False, "error": "Reservation is not in reserved status"}), 400
        
        reservations_collection.update_one(
            {"_id": ObjectId(reservation_id)},
            {"$set": {"status": "confirmed", "confirmed_at": datetime.utcnow()}}
        )
        
        products_collection.update_one(
            {"_id": reservation['product_id']},
            {
                "$inc": {
                    "stock_quantity": -reservation['quantity'],
                    "reserved_quantity": -reservation['quantity']
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return jsonify({
            "confirmed": True,
            "reservation_id": str(reservation_id),
            "product_id": str(reservation['product_id']),
            "quantity": reservation['quantity']
        }), 200
        
    except Exception as e:
        return jsonify({"confirmed": False, "error": str(e)}), 500

@app.route('/reservations/<reservation_id>/cancel', methods=['POST'])
def cancel_reservation(reservation_id):
    try:
        if not ObjectId.is_valid(reservation_id):
            return jsonify({"cancelled": False, "error": "Invalid reservation ID"}), 400
        
        reservation = reservations_collection.find_one({"_id": ObjectId(reservation_id)})
        if not reservation:
            return jsonify({"cancelled": False, "error": "Reservation not found"}), 404
        
        if reservation['status'] not in ['reserved']:
            return jsonify({"cancelled": False, "error": "Reservation cannot be cancelled"}), 400
        
        reservations_collection.update_one(
            {"_id": ObjectId(reservation_id)},
            {"$set": {"status": "cancelled", "cancelled_at": datetime.utcnow()}}
        )
        
        products_collection.update_one(
            {"_id": reservation['product_id']},
            {
                "$inc": {
                    "reserved_quantity": -reservation['quantity'],
                    "available_quantity": reservation['quantity']
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return jsonify({
            "cancelled": True,
            "reservation_id": str(reservation_id),
            "product_id": str(reservation['product_id']),
            "quantity": reservation['quantity']
        }), 200
        
    except Exception as e:
        return jsonify({"cancelled": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6003))
    app.run(host='0.0.0.0', port=port, debug=True) 