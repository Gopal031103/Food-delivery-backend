# API Reference

Complete API reference for the Food Delivery Management System.

## Overview

- **Base URL**: `http://localhost:8000` (development) or `https://your-domain.com` (production)
- **API Version**: 1.0.0
- **Authentication**: JWT Bearer Token
- **Content-Type**: application/json
- **Default Limit**: 10 items per page
- **Max Limit**: 100 items per page

## Authentication

### Request Headers

```
Authorization: Bearer {token}
Content-Type: application/json
```

### Response Format

All successful responses return HTTP status codes:
- `200 OK`: Successful GET/PUT request
- `201 Created`: Successful POST request
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "status_code": 400,
  "timestamp": "2024-01-01T10:00:00",
  "path": "/endpoint"
}
```

## Authentication Endpoints

### Register User

Creates a new user account.

```
POST /auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "password": "SecurePass123!"
}
```

**Response: 201 Created**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "role": "customer",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

**Validation Rules**:
- Name: 2-255 characters
- Email: Valid email format
- Phone: 10+ digits
- Password: 8+ characters, 1 uppercase, 1 digit, 1 special character
- Email must be unique

### Login

Authenticate user and receive JWT token.

```
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response: 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors**:
- `401 Unauthorized`: Invalid email or password
- `404 Not Found`: User not found

## User Endpoints

### Get Current User

Get the profile of the authenticated user.

```
GET /users/me
Authorization: Bearer {token}
```

**Response: 200 OK**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "role": "customer",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

### Get User by ID

Get a user's profile by ID.

```
GET /users/{user_id}
Authorization: Bearer {token}
```

**Parameters**:
- `user_id` (path, required): User ID

**Response: 200 OK**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "role": "customer",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

**Permissions**: 
- Users can view their own profile
- Admins can view any user profile

**Errors**:
- `404 Not Found`: User not found
- `403 Forbidden`: Permission denied

### Update User Profile

Update user's profile information.

```
PUT /users/{user_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Jane Doe",
  "phone": "9876543211"
}
```

**Parameters**:
- `user_id` (path, required): User ID

**Request Body** (all optional):
- `name`: 2-255 characters
- `phone`: 10+ digits

**Response: 200 OK**
```json
{
  "id": 1,
  "name": "Jane Doe",
  "email": "john@example.com",
  "phone": "9876543211",
  "role": "customer",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:30:00"
}
```

**Permissions**:
- Users can update their own profile
- Admins can update any user profile

### List Users (Admin Only)

Get paginated list of all users.

```
GET /users?skip=0&limit=10
Authorization: Bearer {admin_token}
```

**Query Parameters**:
- `skip` (optional, default=0): Number of records to skip
- `limit` (optional, default=10, max=100): Records per page

**Response: 200 OK**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210",
    "role": "customer",
    "created_at": "2024-01-01T10:00:00"
  }
]
```

**Permissions**: Admin only

**Errors**:
- `403 Forbidden`: User is not admin

### Delete User (Admin Only)

Delete a user account.

```
DELETE /users/{user_id}
Authorization: Bearer {admin_token}
```

**Parameters**:
- `user_id` (path, required): User ID

**Response: 204 No Content**

**Permissions**: Admin only

**Errors**:
- `404 Not Found`: User not found
- `403 Forbidden`: User is not admin

## Restaurant Endpoints

### Create Restaurant

Create a new restaurant.

```
POST /restaurants
Authorization: Bearer {token}
Content-Type: application/json

{
  "restaurant_name": "Pizza Palace",
  "address": "123 Main Street",
  "city": "New York",
  "phone": "9876543212",
  "email": "pizza@example.com"
}
```

**Request Body** (all required except email):
- `restaurant_name`: 3-255 characters
- `address`: 5-500 characters
- `city`: 2-100 characters
- `phone`: 10+ digits
- `email`: Valid email (optional)

**Response: 201 Created**
```json
{
  "id": 1,
  "owner_id": 1,
  "restaurant_name": "Pizza Palace",
  "address": "123 Main Street",
  "city": "New York",
  "phone": "9876543212",
  "email": "pizza@example.com",
  "rating": 0.0,
  "is_active": true,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

**Permissions**: Any authenticated user

### List Restaurants

Get paginated list of active restaurants.

```
GET /restaurants?skip=0&limit=10&city=New%20York
```

**Query Parameters**:
- `skip` (optional, default=0): Records to skip
- `limit` (optional, default=10): Records per page
- `city` (optional): Filter by city name

**Response: 200 OK**
```json
[
  {
    "id": 1,
    "owner_id": 1,
    "restaurant_name": "Pizza Palace",
    "address": "123 Main Street",
    "city": "New York",
    "phone": "9876543212",
    "email": "pizza@example.com",
    "rating": 4.5,
    "is_active": true,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  }
]
```

**Permissions**: Public (no authentication required)

### Get Restaurant

Get restaurant details by ID.

```
GET /restaurants/{restaurant_id}
```

**Parameters**:
- `restaurant_id` (path, required): Restaurant ID

**Response: 200 OK**
```json
{
  "id": 1,
  "owner_id": 1,
  "restaurant_name": "Pizza Palace",
  "address": "123 Main Street",
  "city": "New York",
  "phone": "9876543212",
  "email": "pizza@example.com",
  "rating": 4.5,
  "is_active": true,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

**Errors**:
- `404 Not Found`: Restaurant not found

### Update Restaurant

Update restaurant details.

```
PUT /restaurants/{restaurant_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "restaurant_name": "Pizza Palace Pro",
  "city": "New York"
}
```

**Parameters**:
- `restaurant_id` (path, required): Restaurant ID

**Request Body** (all optional):
- `restaurant_name`: 3-255 characters
- `address`: 5-500 characters
- `city`: 2-100 characters
- `phone`: 10+ digits
- `email`: Valid email

**Response: 200 OK**

**Permissions**:
- Owner of the restaurant
- Admin users

**Errors**:
- `404 Not Found`: Restaurant not found
- `403 Forbidden`: Permission denied

### Delete Restaurant

Delete a restaurant.

```
DELETE /restaurants/{restaurant_id}
Authorization: Bearer {token}
```

**Parameters**:
- `restaurant_id` (path, required): Restaurant ID

**Response: 204 No Content**

**Permissions**:
- Owner of the restaurant
- Admin users

### Activate Restaurant (Admin Only)

Activate an inactive restaurant.

```
PUT /restaurants/{restaurant_id}/activate
Authorization: Bearer {admin_token}
```

**Response: 200 OK**

### Deactivate Restaurant (Admin Only)

Deactivate an active restaurant.

```
PUT /restaurants/{restaurant_id}/deactivate
Authorization: Bearer {admin_token}
```

**Response: 200 OK**

## Menu Endpoints

### Create Menu Item

Add an item to restaurant menu.

```
POST /menu?restaurant_id=1
Authorization: Bearer {owner_token}
Content-Type: application/json

{
  "food_name": "Margherita Pizza",
  "description": "Classic pizza with tomato and mozzarella",
  "category": "Pizza",
  "price": 299.99
}
```

**Query Parameters**:
- `restaurant_id` (required): Restaurant ID

**Request Body** (all required except description):
- `food_name`: 2-255 characters
- `description`: Optional, max 1000 characters
- `category`: 2-100 characters
- `price`: Positive number

**Response: 201 Created**
```json
{
  "id": 1,
  "restaurant_id": 1,
  "food_name": "Margherita Pizza",
  "description": "Classic pizza",
  "category": "Pizza",
  "price": 299.99,
  "available": true,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

**Permissions**: Restaurant owner

### List Menu Items

Get menu items for a restaurant.

```
GET /menu?restaurant_id=1&skip=0&limit=10&category=Pizza
```

**Query Parameters**:
- `restaurant_id` (required): Restaurant ID
- `skip` (optional, default=0): Records to skip
- `limit` (optional, default=10): Records per page
- `category` (optional): Filter by category

**Response: 200 OK**
```json
[
  {
    "id": 1,
    "restaurant_id": 1,
    "food_name": "Margherita Pizza",
    "description": "Classic pizza",
    "category": "Pizza",
    "price": 299.99,
    "available": true,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  }
]
```

### Get Menu Item

Get menu item details.

```
GET /menu/{menu_item_id}
```

**Parameters**:
- `menu_item_id` (path, required): Menu item ID

**Response: 200 OK**

### Update Menu Item

Update menu item details.

```
PUT /menu/{menu_item_id}
Authorization: Bearer {owner_token}
Content-Type: application/json

{
  "price": 349.99,
  "available": true
}
```

**Response: 200 OK**

**Permissions**: Restaurant owner

### Delete Menu Item

Delete a menu item.

```
DELETE /menu/{menu_item_id}
Authorization: Bearer {owner_token}
```

**Response: 204 No Content**

**Permissions**: Restaurant owner

## Order Endpoints

### Create Order

Place a new order.

```
POST /orders
Authorization: Bearer {customer_token}
Content-Type: application/json

{
  "restaurant_id": 1,
  "delivery_address": "456 Oak Avenue",
  "items": [
    {
      "menu_item_id": 1,
      "quantity": 2
    },
    {
      "menu_item_id": 2,
      "quantity": 1
    }
  ]
}
```

**Request Body**:
- `restaurant_id` (required): Restaurant ID
- `delivery_address` (required): 5-500 characters
- `items` (required): Array with at least 1 item
  - `menu_item_id`: Menu item ID
  - `quantity`: Positive integer

**Response: 201 Created**
```json
{
  "id": 1,
  "user_id": 1,
  "restaurant_id": 1,
  "total_amount": 599.98,
  "order_status": "pending",
  "delivery_address": "456 Oak Avenue",
  "items": [
    {
      "id": 1,
      "order_id": 1,
      "menu_item_id": 1,
      "quantity": 2,
      "item_price": 299.99
    }
  ],
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

**Permissions**: Customer

### List Orders

Get orders with pagination.

```
GET /orders?skip=0&limit=10&status=pending
Authorization: Bearer {token}
```

**Query Parameters**:
- `skip` (optional): Records to skip
- `limit` (optional): Records per page
- `status` (optional): Filter by status

**Order Status Values**:
- `pending`: Order created
- `confirmed`: Payment completed
- `preparing`: Restaurant preparing
- `on_the_way`: Order in transit
- `delivered`: Order delivered
- `cancelled`: Order cancelled

**Response: 200 OK**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "restaurant_id": 1,
    "total_amount": 599.98,
    "order_status": "pending",
    "delivery_address": "456 Oak Avenue",
    "items": [...],
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  }
]
```

**Permissions**:
- Customers see only their orders
- Restaurant owners see orders for their restaurants
- Admins see all orders

### Get Order

Get order details.

```
GET /orders/{order_id}
Authorization: Bearer {token}
```

**Response: 200 OK**

### Update Order Status

Update order status.

```
PUT /orders/{order_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "order_status": "preparing"
}
```

**Permissions**:
- Customers can only cancel pending orders
- Restaurant owners can update status
- Admins can update status

**Errors**:
- `422 Unprocessable Entity`: Invalid status transition

### Delete Order (Admin Only)

Delete an order.

```
DELETE /orders/{order_id}
Authorization: Bearer {admin_token}
```

**Response: 204 No Content**

## Payment Endpoints

### Create Payment

Create payment for an order.

```
POST /payments
Authorization: Bearer {customer_token}
Content-Type: application/json

{
  "order_id": 1,
  "payment_method": "credit_card"
}
```

**Request Body**:
- `order_id` (required): Order ID
- `payment_method` (required): One of:
  - `credit_card`
  - `debit_card`
  - `upi`
  - `net_banking`
  - `wallet`
  - `cod`

**Response: 201 Created**
```json
{
  "id": 1,
  "order_id": 1,
  "payment_method": "credit_card",
  "payment_status": "pending",
  "transaction_id": "TXN-1-1",
  "amount": 599.98,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

**Permissions**: Order owner

**Errors**:
- `404 Not Found`: Order not found
- `409 Conflict`: Payment already exists
- `422 Unprocessable Entity`: Order already cancelled

### List Payments

Get paginated payments.

```
GET /payments?skip=0&limit=10&status=completed
Authorization: Bearer {token}
```

**Query Parameters**:
- `skip` (optional): Records to skip
- `limit` (optional): Records per page
- `status` (optional): Filter by status

**Payment Status Values**:
- `pending`: Awaiting processing
- `completed`: Payment successful
- `failed`: Payment failed
- `refunded`: Payment refunded

**Response: 200 OK**

### Get Payment

Get payment details.

```
GET /payments/{payment_id}
Authorization: Bearer {token}
```

**Response: 200 OK**

### Update Payment Status (Admin Only)

Update payment status.

```
PUT /payments/{payment_id}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "status": "completed"
}
```

**Response: 200 OK**

**Side Effects**:
- `completed`: Order status → `preparing`
- `failed`: Order status → `pending`
- `refunded`: Order status → `cancelled`

## Pagination

All list endpoints support pagination:

```
GET /endpoint?skip=0&limit=10
```

**Parameters**:
- `skip`: Records to skip (default: 0)
- `limit`: Records to return (default: 10, max: 100)

**Response includes**:
- Array of items
- Total count
- Current page
- Has next/previous page flags

## Rate Limiting

- Development: No rate limiting
- Production: Recommended 100 requests/minute per user

## CORS

CORS is enabled for all origins in development. Configure for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
)
```

## Health Check

Monitor API health:

```
GET /health
```

**Response: 200 OK**
```json
{
  "status": "healthy",
  "service": "Food Delivery Management System",
  "version": "1.0.0",
  "timestamp": "2024-01-01T10:00:00"
}
```

## API Documentation

- **Swagger/OpenAPI**: /api/docs
- **ReDoc**: /api/redoc

Generated automatically from code docstrings and schemas.
