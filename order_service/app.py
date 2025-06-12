from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)


mongo_uri = os.environ.get('MONGO_URI', 'mongodb://admin:password123@localhost:27017/klea_ecommerce_order?authSource=admin')
client = MongoClient(mongo_uri)
db = client.klea_ecommerce_order
orders_collection = db.orders

@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        
        required_fields = ['customer_id', 'products', 'total_amount']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400
        
        if not isinstance(data['products'], list) or len(data['products']) == 0:
            return jsonify({"error": "products must be a non-empty list"}), 400
        
        for product in data['products']:
            if not all(key in product for key in ['product_id', 'quantity', 'price']):
                return jsonify({"error": "Each product must have product_id, quantity, and price"}), 400
        
        order_data = {
            "customer_id": data['customer_id'],
            "products": data['products'],
            "total_amount": float(data['total_amount']),
            "currency": data.get('currency', 'USD'),
            "status": data.get('status', 'pending'),
            "payment_id": data.get('payment_id'),
            "reservation_ids": data.get('reservation_ids', []),
            "shipping_address": data.get('shipping_address'),
            "billing_address": data.get('billing_address'),
            "order_notes": data.get('order_notes', ''),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = orders_collection.insert_one(order_data)
        
        return jsonify({
            "message": "Order created successfully",
            "order_id": str(result.inserted_id),
            "status": order_data['status'],
            "total_amount": order_data['total_amount']
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    try:
        if not ObjectId.is_valid(order_id):
            return jsonify({"error": "Invalid order ID"}), 400
            
        order = orders_collection.find_one({"_id": ObjectId(order_id)})
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        order['_id'] = str(order['_id'])
        return jsonify(order), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    try:
        if not ObjectId.is_valid(order_id):
            return jsonify({"error": "Invalid order ID"}), 400
            
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({"error": "status is required"}), 400
        
        valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({"error": f"Invalid status. Valid statuses: {valid_statuses}"}), 400
        
        update_data = {
            "status": new_status,
            "updated_at": datetime.utcnow()
        }
        
        # Add timestamp for specific status changes
        if new_status == 'confirmed':
            update_data['confirmed_at'] = datetime.utcnow()
        elif new_status == 'shipped':
            update_data['shipped_at'] = datetime.utcnow()
        elif new_status == 'delivered':
            update_data['delivered_at'] = datetime.utcnow()
        elif new_status == 'cancelled':
            update_data['cancelled_at'] = datetime.utcnow()
        
        result = orders_collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Order not found"}), 404
        
        return jsonify({
            "message": "Order status updated successfully",
            "order_id": order_id,
            "status": new_status
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/orders/customer/<customer_id>', methods=['GET'])
def get_customer_orders(customer_id):
    try:
        # Get query parameters for filtering
        status = request.args.get('status')
        
        # Build query
        query = {"customer_id": customer_id}
        if status:
            query["status"] = status
        
        # Get orders
        orders = list(orders_collection.find(query)
                     .sort("created_at", -1))
        
        for order in orders:
            order['_id'] = str(order['_id'])
        
        return jsonify({
            "orders": orders
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/orders', methods=['GET'])
def get_all_orders():
    try:
        status = request.args.get('status')
        customer_id = request.args.get('customer_id')
        
        query = {}
        if status:
            query["status"] = status
        if customer_id:
            query["customer_id"] = customer_id
        
        orders = list(orders_collection.find(query)
                     .sort("created_at", -1))
        
        for order in orders:
            order['_id'] = str(order['_id'])
        
        return jsonify({
            "orders": orders
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6005))
    app.run(host='0.0.0.0', port=port, debug=True) 