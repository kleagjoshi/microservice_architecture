from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import uuid
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)

mongo_uri = os.environ.get('MONGO_URI', 'mongodb://admin:password123@localhost:27017/klea_ecommerce_payment?authSource=admin')
client = MongoClient(mongo_uri)
db = client.klea_ecommerce_payment
payments_collection = db.payments

@app.route('/payments/process', methods=['POST'])
def process_payment():
    try:
        data = request.get_json()
        
        required_fields = ['customer_id', 'amount', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"{field} is required"}), 400
        
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({"success": False, "error": "Amount must be greater than 0"}), 400
        
        # Simulate payment processing
        # In a real system, this would integrate with payment providers like Stripe, PayPal, etc.
        payment_success = simulate_payment_processing(data['payment_method'], amount)
        
        payment_data = {
            "customer_id": data['customer_id'],
            "amount": amount,
            "currency": data.get('currency', 'USD'),
            "payment_method": data['payment_method'],
            "status": "completed" if payment_success else "failed",
            "transaction_id": str(uuid.uuid4()),
            "gateway_response": {
                "success": payment_success,
                "message": "Payment processed successfully" if payment_success else "Payment failed"
            },
            "order_id": data.get('order_id'),
            "created_at": datetime.utcnow()
        }
        
        result = payments_collection.insert_one(payment_data)
        
        response_data = {
            "success": payment_success,
            "payment_id": str(result.inserted_id),
            "transaction_id": payment_data['transaction_id'],
            "amount": amount,
            "currency": payment_data['currency'],
            "status": payment_data['status']
        }
        
        if not payment_success:
            response_data["error"] = "Payment processing failed"
        
        status_code = 200 if payment_success else 400
        return jsonify(response_data), status_code
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/payments/<payment_id>', methods=['GET'])
def get_payment(payment_id):
    try:
        if not ObjectId.is_valid(payment_id):
            return jsonify({"error": "Invalid payment ID"}), 400
            
        payment = payments_collection.find_one({"_id": ObjectId(payment_id)})
        if not payment:
            return jsonify({"error": "Payment not found"}), 404
        
        payment['_id'] = str(payment['_id'])
        return jsonify(payment), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/payments/customer/<customer_id>', methods=['GET'])
def get_customer_payments(customer_id):
    try:
        payments = list(payments_collection.find({"customer_id": customer_id}))
        for payment in payments:
            payment['_id'] = str(payment['_id'])
        
        return jsonify(payments), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def simulate_payment_processing(payment_method, amount):
    """
    Simulate payment processing logic.
    In a real system, this would integrate with actual payment gateways.
    """
    # Simulate some failures for testing
    if payment_method == "invalid_card":
        return False
    if amount > 10000:  # Simulate failure for very large amounts
        return False
    
    return True

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6004))
    app.run(host='0.0.0.0', port=port, debug=True) 