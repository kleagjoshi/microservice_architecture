In this assignment I created 5 microservices which aligns with an ecommerce scenario. 

Auth Service
  This service includes user registration and login, password hashing with SHA256 and JWT token generation and validation.

Customer Service
  This service includes customer data management(CRUD) and customer validation for orders.

Inventory Service
  This service includes product catalog management, stock availability checking and reservation handling.

Order Service
  This service includes order creation and management.

Payment Service
  This service includes payment record management and payment processing simulation. In a real system we would have some bank transactions, checks etc; here I have simulated a function to mimic this step.

Database 
  I have user our shared mongoDB instance for each of the services. You can find them under the name "klea_ecommerce_{service_name}"

Api Gateaway
  Api Gateaway exposes an endpoint "create_order" that follows this flow:
    1. Authenticate/authorize customer token
    2. Validate customer exists
    3. Check product availability & reserve stock
    4. Process payment
    5. Create order record
    6. Return order confirmation

  I have also implemented some error handling logic:
    1. If payment fails, automatically cancel stock reservations
    2. 5-second timeouts for inter-service communication
    

AI Prompts used:

   - I prompted ai to generate some script to populate the database with some dummy data. It resulted sucessful to not waste time with data entry.
   - I prompted to generate a function which mimics payment processing, provided a simple functions with basic checks.
   - I prompted to generate some /create_order sample requests to complete all possible cases. Results are shown in "ORDER_TEST_CASES.md"


### How to test

1. Create .env file with MongoDB credentials (our shared instance).

2. Start the containers
```bash
docker-compose up -d --build
```

3. Test api gateaway

  1. Login with an already created user to get token

```bash
curl -X POST http://localhost:9080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "klea",
    "password": "password123"
  }'
```
Save the returned token for use in subsequent requests.



  2. Create an order using what you created above

```bash
curl -X POST http://localhost:9080/api/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "token": "{generated_token_from_login}",
    "customer_id": "6849dd2562e5fa1c135a04fb",
    "products": [
      {
        "product_id": "6849dd2a5b6717b8055f93a9",
        "quantity": 1
      },
      {
        "product_id": "6849dd2b5b6717b8055f93aa",
        "quantity": 2
      }
    ],
    "payment_method": "credit_card",
    "shipping_address": "123 Main St, City, State 12345",
    "billing_address": "123 Main St, City, State 12345"
  }'
```

In "ORDER_TEST_CASES.md" you will find a detailed list of different test cases that covers the complete logic in this system. 