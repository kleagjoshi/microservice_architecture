from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5001')
CUSTOMER_SERVICE_URL = os.environ.get('CUSTOMER_SERVICE_URL', 'http://localhost:5002')
INVENTORY_SERVICE_URL = os.environ.get('INVENTORY_SERVICE_URL', 'http://localhost:5003')
PAYMENT_SERVICE_URL = os.environ.get('PAYMENT_SERVICE_URL', 'http://localhost:5004')
ORDER_SERVICE_URL = os.environ.get('ORDER_SERVICE_URL', 'http://localhost:5005')


@app.route('/api/create_order', methods=['POST'])
def create_order():
    """
    1. Authenticate/authorize customer token
    2. Validate customer exists
    3. Check product availability & reserve stock
    4. Process payment
    5. Create order record
    6. Return order confirmation
    """
    try:
        data = request.get_json()
        
        token = data.get('token')
        customer_id = data.get('customer_id')
        products = data.get('products')
        payment_method = data.get('payment_method')
        
        if not all([token, customer_id, products, payment_method]):
            return jsonify({
                "success": False,
                "error": "token, customer_id, products, and payment_method are required"
            }), 400
        
        # Authenticate/authorize customer token
        auth_response = authenticate_token(token)
        if not auth_response['success']:
            return jsonify({
                "success": False,
                "error": "Authentication failed",
                "details": auth_response['error']
            }), 401
        
        authenticated_user_id = auth_response['user_id']
        
        # Validate customer exists
        customer_response = validate_customer(customer_id)
        if not customer_response['success']:
            return jsonify({
                "success": False,
                "error": "Customer validation failed",
                "details": customer_response['error']
            }), 400
        
        customer_info = customer_response['data']
        
        # Check product availability & reserve stock
        reservation_ids = []
        total_amount = 0
        
        for product in products:
            product_id = product['product_id']
            quantity = product['quantity']
            
            # Get product details first to get price
            product_details = get_product_details(product_id)
            if not product_details['success']:
                cancel_reservations(reservation_ids)
                return jsonify({
                    "success": False,
                    "error": f"Product {product_id} not found",
                    "details": product_details['error']
                }), 400
            
            # Check availability
            availability_response = check_product_availability(product_id, quantity)
            if not availability_response['success']:
                cancel_reservations(reservation_ids)
                return jsonify({
                    "success": False,
                    "error": f"Product {product_id} is not available",
                    "details": availability_response['error']
                }), 400
            
            # Reserve stock
            reservation_response = reserve_product_stock(product_id, quantity, customer_id)
            if not reservation_response['success']:
                cancel_reservations(reservation_ids)
                return jsonify({
                    "success": False,
                    "error": f"Failed to reserve stock for product {product_id}",
                    "details": reservation_response['error']
                }), 400
            
            reservation_ids.append(reservation_response['reservation_id'])
            total_amount += product_details['data']['price'] * quantity
        
        # Process payment
        payment_response = process_payment(customer_id, total_amount, payment_method)
        if not payment_response['success']:
            cancel_reservations(reservation_ids)
            return jsonify({
                "success": False,
                "error": "Payment processing failed",
                "details": payment_response['error']
            }), 400
        
        payment_id = payment_response['payment_id']
        
        # Create order record
        order_data = {
            "customer_id": customer_id,
            "products": [{"product_id": p['product_id'], "quantity": p['quantity'], "price": get_product_details(p['product_id'])['data']['price']} for p in products],
            "total_amount": total_amount,
            "payment_id": payment_id,
            "reservation_ids": reservation_ids,
            "status": "confirmed",
            "shipping_address": data.get('shipping_address'),
            "billing_address": data.get('billing_address')
        }
        
        order_response = create_order_record(order_data)
        if not order_response['success']:
            return jsonify({
                "success": False,
                "error": "Order creation failed",
                "details": order_response['error'],
                "payment_id": payment_id,
                "reservation_ids": reservation_ids
            }), 500
        
        order_id = order_response['order_id']
        
        # Confirm reservations
        confirm_reservations(reservation_ids)
        
        return jsonify({
            "success": True,
            "message": "Order created successfully",
            "order_confirmation": {
                "order_id": order_id,
                "customer_id": customer_id,
                "customer_name": customer_info['name'],
                "products": products,
                "total_amount": total_amount,
                "payment_id": payment_id,
                "status": "confirmed",
                "created_at": datetime.utcnow().isoformat()
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

def authenticate_token(token):
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/verify",
            json={"token": token},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "user_id": data['user_id'],
                "username": data['username']
            }
        else:
            return {
                "success": False,
                "error": response.json().get('error', 'Authentication failed')
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Auth service error: {str(e)}"
        }

def validate_customer(customer_id):
    try:
        response = requests.get(
            f"{CUSTOMER_SERVICE_URL}/customers/{customer_id}/validate",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": data['valid'],
                "data": {
                    "customer_id": data['customer_id'],
                    "name": data['name'],
                    "email": data['email']
                }
            }
        else:
            return {
                "success": False,
                "error": response.json().get('error', 'Customer validation failed')
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Customer service error: {str(e)}"
        }

def get_product_details(product_id):
    try:
        response = requests.get(
            f"{INVENTORY_SERVICE_URL}/products/{product_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "data": {
                    "product_id": data['_id'],
                    "name": data['name'],
                    "price": data['price']
                }
            }
        else:
            return {
                "success": False,
                "error": response.json().get('error', 'Product not found')
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Inventory service error: {str(e)}"
        }

def check_product_availability(product_id, quantity):
    try:
        response = requests.get(
            f"{INVENTORY_SERVICE_URL}/products/{product_id}/availability",
            params={"quantity": quantity},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": data['available'],
                "data": {
                    "product_id": data['product_id'],
                    "available_quantity": data['available_quantity']
                }
            }
        else:
            return {
                "success": False,
                "error": response.json().get('error', 'Availability check failed')
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Inventory service error: {str(e)}"
        }

def reserve_product_stock(product_id, quantity, customer_id):
    try:
        response = requests.post(
            f"{INVENTORY_SERVICE_URL}/products/{product_id}/reserve",
            json={"quantity": quantity, "customer_id": customer_id},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": data['reserved'],
                "reservation_id": data['reservation_id']
            }
        else:
            return {
                "success": False,
                "error": response.json().get('error', 'Stock reservation failed')
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Inventory service error: {str(e)}"
        }

def process_payment(customer_id, amount, payment_method):
    try:
        response = requests.post(
            f"{PAYMENT_SERVICE_URL}/payments/process",
            json={
                "customer_id": customer_id,
                "amount": amount,
                "payment_method": payment_method,
                "currency": "USD"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": data['success'],
                "payment_id": data['payment_id'],
                "transaction_id": data['transaction_id']
            }
        else:
            return {
                "success": False,
                "error": response.json().get('error', 'Payment processing failed')
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Payment service error: {str(e)}"
        }

def create_order_record(order_data):
    try:
        response = requests.post(
            f"{ORDER_SERVICE_URL}/orders",
            json=order_data,
            timeout=5
        )
        
        if response.status_code == 201:
            data = response.json()
            return {
                "success": True,
                "order_id": data['order_id']
            }
        else:
            return {
                "success": False,
                "error": response.json().get('error', 'Order creation failed')
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Order service error: {str(e)}"
        }

def cancel_reservations(reservation_ids):
    for reservation_id in reservation_ids:
        try:
            requests.post(
                f"{INVENTORY_SERVICE_URL}/reservations/{reservation_id}/cancel",
                timeout=5
            )
        except Exception as e:
            print(f"Failed to cancel reservation {reservation_id}: {str(e)}")

def confirm_reservations(reservation_ids):
    for reservation_id in reservation_ids:
        try:
            requests.post(
                f"{INVENTORY_SERVICE_URL}/reservations/{reservation_id}/confirm",
                timeout=5
            )
        except Exception as e:
            print(f"Failed to confirm reservation {reservation_id}: {str(e)}")

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Proxy to auth service for user login"""
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/login",
            json=request.get_json(),
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9080))
    app.run(host='0.0.0.0', port=port, debug=True) 