## Test Case Categories

### 1. ✅ Successful Order Creation

#### Test 1.1: Basic Successful Order
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [
      {
        "product_id": "6849dd2a5b6717b8055f93a9",
        "quantity": 1
      }
    ],
    "payment_method": "credit_card",
    "shipping_address": "123 Main St, City, State 12345",
    "billing_address": "123 Main St, City, State 12345"
  }'
```
**Expected**: 201 Created with order confirmation

#### Test 1.2: Multiple Products Order
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [
      {
        "product_id": "6849dd2a5b6717b8055f93a9",
        "quantity": 1
      },
      {
        "product_id": "6849dd2b5b6717b8055f93aa",
        "quantity": 2
      },
      {
        "product_id": "6849dd2c5b6717b8055f93ab",
        "quantity": 1
      }
    ],
    "payment_method": "debit_card",
    "shipping_address": "456 Oak Ave, Boston, MA 02101",
    "billing_address": "456 Oak Ave, Boston, MA 02101"
  }'
```
**Expected**: 201 Created with multiple products in order

#### Test 1.3: Different Payment Methods
```bash
# PayPal
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [{"product_id": "6849dd2b5b6717b8055f93aa", "quantity": 1}],
    "payment_method": "paypal",
    "shipping_address": "789 Pine St, Seattle, WA 98101",
    "billing_address": "789 Pine St, Seattle, WA 98101"
  }'
```
**Expected**: 201 Created with PayPal payment

### 2. 🔒 Authentication & Authorization Errors

#### Test 2.1: Missing Token
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [{"product_id": "6849dd2a5b6717b8055f93a9", "quantity": 1}],
    "payment_method": "credit_card"
  }'
```
**Expected**: 400 Bad Request - "token is required"

#### Test 2.2: Invalid Token
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "invalid.token.here",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [{"product_id": "6849dd2a5b6717b8055f93a9", "quantity": 1}],
    "payment_method": "credit_card"
  }'
```
**Expected**: 401 Unauthorized - "Authentication failed"

#### Test 2.3: Expired Token
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNjQ5ODMxMjY3fQ.expired_token_signature",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [{"product_id": "6849dd2a5b6717b8055f93a9", "quantity": 1}],
    "payment_method": "credit_card"
  }'
```
**Expected**: 401 Unauthorized - "Token has expired"

### 3. 👤 Customer Validation Errors

#### Test 3.1: Missing Customer ID
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "products": [{"product_id": "6849dd2a5b6717b8055f93a9", "quantity": 1}],
    "payment_method": "credit_card"
  }'
```
**Expected**: 400 Bad Request - "customer_id is required"

#### Test 3.2: Invalid Customer ID
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "invalid_customer_id",
    "products": [{"product_id": "6849dd2a5b6717b8055f93a9", "quantity": 1}],
    "payment_method": "credit_card"
  }'
```
**Expected**: 400 Bad Request - "Customer validation failed"

#### Test 3.3: Non-existent Customer
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "684900000000000000000000",
    "products": [{"product_id": "6849dd2a5b6717b8055f93a9", "quantity": 1}],
    "payment_method": "credit_card"
  }'
```
**Expected**: 400 Bad Request - "Customer validation failed"

### 4. 📦 Product & Inventory Errors

#### Test 4.1: Missing Products
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "payment_method": "credit_card"
  }'
```
**Expected**: 400 Bad Request - "products is required"

#### Test 4.2: Empty Products Array
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [],
    "payment_method": "credit_card"
  }'
```
**Expected**: 400 Bad Request - "products is required"

#### Test 4.3: Invalid Product ID
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [{"product_id": "invalid_product_id", "quantity": 1}],
    "payment_method": "credit_card"
  }'
```
**Expected**: 400 Bad Request - "Product invalid_product_id not found"

#### Test 4.4: Non-existent Product
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [{"product_id": "684900000000000000000000", "quantity": 1}],
    "payment_method": "credit_card"
  }'
```
**Expected**: 400 Bad Request - "Product not found"

#### Test 4.5: Insufficient Stock
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [{"product_id": "6849dd2a5b6717b8055f93a9", "quantity": 999}],
    "payment_method": "credit_card"
  }'
```
**Expected**: 400 Bad Request - "Product is not available"

#### Test 4.6: Zero Quantity
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [{"product_id": "6849dd2a5b6717b8055f93a9", "quantity": 0}],
    "payment_method": "credit_card"
  }'
```
**Expected**: 400 Bad Request - Product availability check should fail

### 5. 💳 Payment Errors

#### Test 5.1: Missing Payment Method
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [{"product_id": "6849dd2a5b6717b8055f93a9", "quantity": 1}]
  }'
```
**Expected**: 400 Bad Request - "payment_method is required"

#### Test 5.2: Invalid Payment Method
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [{"product_id": "6849dd2a5b6717b8055f93a9", "quantity": 1}],
    "payment_method": "invalid_card"
  }'
```
**Expected**: 400 Bad Request - "Payment processing failed"

#### Test 5.3: Large Amount Payment (Simulated Failure)
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [{"product_id": "6849dd2a5b6717b8055f93a9", "quantity": 10}],
    "payment_method": "credit_card"
  }'
```
**Expected**: 400 Bad Request - Payment might fail for amounts > $10,000

### 6. 🔄 Rollback Scenarios

#### Test 6.1: Payment Failure After Stock Reservation
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [{"product_id": "6849dd2a5b6717b8055f93a9", "quantity": 1}],
    "payment_method": "invalid_card"
  }'
```
**Expected**: Stock should be automatically unreserved after payment failure

### 7. 📋 Malformed Request Data

#### Test 7.1: Invalid JSON
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{"token": "valid_token", "customer_id": "valid_id", "products": [{"product_id": "valid_id", "quantity": 1}], "payment_method": "credit_card"'
```
**Expected**: 400 Bad Request - Invalid JSON

#### Test 7.2: Missing Required Fields
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4"
  }'
```
**Expected**: 400 Bad Request - Missing required fields

#### Test 7.3: Wrong Data Types
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": "not_an_array",
    "payment_method": "credit_card"
  }'
```
**Expected**: 400 Bad Request - Invalid data type

### 8. 🌐 Service Unavailability

#### Test 8.1: Auth Service Down
Stop auth service: `docker stop auth_service`
```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [{"product_id": "6849dd2a5b6717b8055f93a9", "quantity": 1}],
    "payment_method": "credit_card"
  }'
```
**Expected**: 401 Unauthorized - Auth service error
**Restore**: `docker start auth_service`

## Test Execution Helper Scripts

### Run All Success Tests
```bash
#!/bin/bash
echo "Running successful order creation tests..."

# Test 1.1: Basic Order
echo "Test 1.1: Basic successful order"
curl -X POST http://localhost:9080/api/create_order -H "Content-Type: application/json" -d '{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4","customer_id":"6849dd2562e5fa1c135a04fb","products":[{"product_id":"6849dd2a5b6717b8055f93a9","quantity":1}],"payment_method":"credit_card","shipping_address":"123 Main St","billing_address":"123 Main St"}'
echo -e "\n---\n"

# Test 1.2: Multiple Products
echo "Test 1.2: Multiple products order"
curl -X POST http://localhost:9080/api/create_order -H "Content-Type: application/json" -d '{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4","customer_id":"6849dd2562e5fa1c135a04fb","products":[{"product_id":"6849dd2a5b6717b8055f93a9","quantity":1},{"product_id":"6849dd2b5b6717b8055f93aa","quantity":1}],"payment_method":"paypal","shipping_address":"456 Oak Ave","billing_address":"456 Oak Ave"}'
echo -e "\n---\n"
```

### Run All Error Tests
```bash
#!/bin/bash
echo "Running error scenario tests..."

# Test 2.1: Missing Token
echo "Test 2.1: Missing token"
curl -X POST http://localhost:9080/api/create_order -H "Content-Type: application/json" -d '{"customer_id":"6849dd2562e5fa1c135a04fb","products":[{"product_id":"6849dd2a5b6717b8055f93a9","quantity":1}],"payment_method":"credit_card"}'
echo -e "\n---\n"

# Test 3.1: Missing Customer ID
echo "Test 3.1: Missing customer_id"
curl -X POST http://localhost:9080/api/create_order -H "Content-Type: application/json" -d '{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0YWZjZDhjNGQ3MWMwZDRjNWM2YzZhIiwidXNlcm5hbWUiOiJrbGVhIiwiZXhwIjoxNzQ5ODMxMjY3fQ.q-ERSdvKzcNTxPJpzaaMxe2wbVUVWicljqcH7hIkxt4","products":[{"product_id":"6849dd2a5b6717b8055f93a9","quantity":1}],"payment_method":"credit_card"}'
echo -e "\n---\n"
```