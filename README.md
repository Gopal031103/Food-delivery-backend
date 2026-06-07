# Food Delivery Management System API

A production-ready backend system for a food delivery platform similar to Swiggy/Zomato, built with FastAPI, MySQL, JWT Authentication, and Docker.

## Features

### 🔐 Authentication
- User registration with email validation
- Secure login with JWT token generation
- Password hashing using bcrypt
- Role-based access control (RBAC)

### 👥 User Management
- Customer profiles
- Restaurant owner profiles
- Admin dashboard access
- User profile updates

### 🍽️ Restaurant Management
- Restaurant registration
- Menu management
- Restaurant activation/deactivation
- Browse restaurants by city

### 🛒 Order Management
- Place orders
- Order tracking
- Order status updates
- Order cancellation

### 💳 Payment Processing
- Multiple payment methods support
- Payment status tracking
- Transaction management

### 🔒 Admin Features
- User management
- Restaurant approval/deactivation
- Order monitoring
- Payment tracking

## Technology Stack

- **Python 3.13**: Latest Python version
- **FastAPI**: Modern, fast web framework
- **MySQL**: Relational database
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation using Python type hints
- **JWT**: Token-based authentication
- **Bcrypt**: Password hashing
- **Docker**: Container orchestration
- **Pytest**: Testing framework
- **Alembic**: Database migrations

## Project Structure

```
food_delivery/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Main FastAPI application
│   ├── config.py                  # Configuration settings
│   ├── database.py                # Database configuration
│   ├── models.py                  # SQLAlchemy models
│   ├── schemas.py                 # Pydantic schemas
│   ├── auth.py                    # JWT & password utilities
│   ├── utils.py                   # Utility functions
│   ├── exceptions.py              # Custom exceptions
│   ├── routers/
│   │   ├── auth.py               # Authentication routes
│   │   ├── users.py              # User management routes
│   │   ├── restaurants.py        # Restaurant routes
│   │   ├── menu.py               # Menu management routes
│   │   ├── orders.py             # Order routes
│   │   └── payments.py           # Payment routes
│   └── services/                  # Business logic services
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration & fixtures
│   ├── test_auth.py              # Authentication tests
│   ├── test_restaurants.py       # Restaurant tests
│   └── test_orders.py            # Order tests
│
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker image definition
├── docker-compose.yml            # Docker Compose configuration
├── .env                          # Environment variables
├── .env.example                  # Example environment variables
└── README.md                     # This file
```

## Database Schema

### Users Table
- `id`: Primary key
- `name`: User's full name
- `email`: Unique email address
- `phone`: Phone number
- `password_hash`: Bcrypt hashed password
- `role`: User role (customer, restaurant_owner, admin)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Restaurants Table
- `id`: Primary key
- `owner_id`: Foreign key to Users
- `restaurant_name`: Name of restaurant
- `address`: Physical address
- `city`: City location
- `phone`: Contact phone
- `email`: Contact email
- `rating`: Average rating
- `is_active`: Active status
- `created_at`: Creation timestamp

### Menu Items Table
- `id`: Primary key
- `restaurant_id`: Foreign key to Restaurants
- `food_name`: Name of food item
- `description`: Item description
- `category`: Food category
- `price`: Item price
- `available`: Availability status
- `created_at`: Creation timestamp

### Orders Table
- `id`: Primary key
- `user_id`: Foreign key to Users
- `restaurant_id`: Foreign key to Restaurants
- `total_amount`: Order total
- `order_status`: Order status (pending, confirmed, preparing, on_the_way, delivered, cancelled)
- `delivery_address`: Delivery location
- `created_at`: Creation timestamp

### Order Items Table
- `id`: Primary key
- `order_id`: Foreign key to Orders
- `menu_item_id`: Foreign key to Menu Items
- `quantity`: Item quantity
- `item_price`: Price at time of order

### Payments Table
- `id`: Primary key
- `order_id`: Foreign key to Orders (unique)
- `payment_method`: Payment method
- `payment_status`: Status (pending, completed, failed, refunded)
- `transaction_id`: Transaction reference
- `amount`: Payment amount
- `created_at`: Creation timestamp

## Installation

### Prerequisites
- Python 3.13
- MySQL 8.0+
- Docker & Docker Compose (optional)

### Local Setup

1. **Clone the repository**
```bash
cd "Food App delivery  Project"
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
# or
source venv/bin/activate      # On Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Copy .env.example to .env and update values
cp .env.example .env
```

5. **Update .env file**
```env
DATABASE_URL=mysql+mysqlconnector://root:root@localhost:3306/food_delivery
SECRET_KEY=your-super-secret-key-min-32-chars-here
DEBUG=True
```

6. **Create MySQL database**
```bash
mysql -u root -p
CREATE DATABASE food_delivery;
EXIT;
```

7. **Run the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Setup

1. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

2. **Access the application**
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

3. **Stop services**
```bash
docker-compose down
```

## API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication Endpoints

#### Register
```http
POST /auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "password": "SecurePass123!"
}

Response: 201 Created
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "role": "customer",
  "created_at": "2024-01-01T10:00:00"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### User Endpoints

#### Get Current User
```http
GET /users/me
Authorization: Bearer {token}

Response: 200 OK
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "role": "customer",
  "created_at": "2024-01-01T10:00:00"
}
```

#### List Users (Admin only)
```http
GET /users?skip=0&limit=10
Authorization: Bearer {admin_token}

Response: 200 OK
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    ...
  }
]
```

#### Update User Profile
```http
PUT /users/{user_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Jane Doe",
  "phone": "9876543211"
}

Response: 200 OK
```

### Restaurant Endpoints

#### Create Restaurant
```http
POST /restaurants
Authorization: Bearer {token}
Content-Type: application/json

{
  "restaurant_name": "Pizza Palace",
  "address": "123 Main St",
  "city": "New York",
  "phone": "9876543212",
  "email": "pizza@example.com"
}

Response: 201 Created
```

#### List Restaurants
```http
GET /restaurants?skip=0&limit=10&city=New%20York

Response: 200 OK
[
  {
    "id": 1,
    "restaurant_name": "Pizza Palace",
    "address": "123 Main St",
    "city": "New York",
    "rating": 4.5,
    "is_active": true,
    ...
  }
]
```

#### Get Restaurant Details
```http
GET /restaurants/{restaurant_id}

Response: 200 OK
```

#### Update Restaurant
```http
PUT /restaurants/{restaurant_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "restaurant_name": "Pizza Palace Pro"
}

Response: 200 OK
```

### Menu Endpoints

#### Add Menu Item
```http
POST /menu?restaurant_id=1
Authorization: Bearer {token}
Content-Type: application/json

{
  "food_name": "Margherita Pizza",
  "description": "Classic pizza with tomato and mozzarella",
  "category": "Pizza",
  "price": 299.99
}

Response: 201 Created
```

#### List Menu Items
```http
GET /menu?restaurant_id=1&skip=0&limit=10&category=Pizza

Response: 200 OK
```

### Order Endpoints

#### Create Order
```http
POST /orders
Authorization: Bearer {customer_token}
Content-Type: application/json

{
  "restaurant_id": 1,
  "delivery_address": "456 Oak Ave",
  "items": [
    {
      "menu_item_id": 1,
      "quantity": 2
    }
  ]
}

Response: 201 Created
```

#### List Orders
```http
GET /orders?skip=0&limit=10&status=pending
Authorization: Bearer {token}

Response: 200 OK
```

#### Get Order Details
```http
GET /orders/{order_id}
Authorization: Bearer {token}

Response: 200 OK
```

#### Update Order Status
```http
PUT /orders/{order_id}
Authorization: Bearer {restaurant_owner_token}
Content-Type: application/json

{
  "order_status": "preparing"
}

Response: 200 OK
```

### Payment Endpoints

#### Create Payment
```http
POST /payments
Authorization: Bearer {customer_token}
Content-Type: application/json

{
  "order_id": 1,
  "payment_method": "credit_card"
}

Response: 201 Created
```

#### List Payments
```http
GET /payments?skip=0&limit=10
Authorization: Bearer {token}

Response: 200 OK
```

#### Get Payment Details
```http
GET /payments/{payment_id}
Authorization: Bearer {token}

Response: 200 OK
```

## Authentication & Authorization

### JWT Token Structure
```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "user_id": 1,
  "email": "john@example.com",
  "role": "customer",
  "exp": 1704110400,
  "iat": 1704109600
}
```

### Using Authorization Header
```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Role-Based Access Control

| Endpoint | Customer | Restaurant Owner | Admin |
|----------|----------|------------------|-------|
| Register | ✅ | ✅ | ✅ |
| Login | ✅ | ✅ | ✅ |
| Create Order | ✅ | ❌ | ✅ |
| View Orders | Own | Restaurant's | All |
| Create Restaurant | ❌ | ✅ | ✅ |
| Update Restaurant | ❌ | Own | ✅ |
| Manage Menu | ❌ | Own Restaurant | ✅ |
| View Users | ❌ | ❌ | ✅ |
| Activate/Deactivate Restaurant | ❌ | ❌ | ✅ |

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_auth.py
```

### Run with coverage
```bash
pytest --cov=app tests/
```

### Run tests with verbose output
```bash
pytest -v
```

## Error Handling

### Response Format for Errors
```json
{
  "detail": "Invalid authentication credentials",
  "error_code": "UNAUTHORIZED",
  "status_code": 401,
  "timestamp": "2024-01-01T10:00:00",
  "path": "/orders"
}
```

### Common Error Codes

| Code | Status | Meaning |
|------|--------|---------|
| VALIDATION_ERROR | 422 | Input validation failed |
| NOT_FOUND | 404 | Resource not found |
| UNAUTHORIZED | 401 | Authentication required |
| FORBIDDEN | 403 | Permission denied |
| DUPLICATE_RESOURCE | 409 | Resource already exists |
| DATABASE_ERROR | 500 | Database operation failed |
| INTERNAL_SERVER_ERROR | 500 | Server error |

## Logging

Logs are configured in the application and can be adjusted via:
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

Logs include:
- Application startup/shutdown
- Database operations
- Authentication events
- Error traces

## Environment Variables

```env
# Database
DATABASE_URL=mysql+mysqlconnector://user:password@host/database
SQLALCHEMY_DATABASE_URL=mysql+mysqlconnector://user:password@host/database

# JWT
SECRET_KEY=your-super-secret-key-at-least-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_NAME=Food Delivery Management System
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## Performance Optimization

1. **Database Connection Pooling**: SQLAlchemy pool_size=10, max_overflow=20
2. **Query Pagination**: Limit results to prevent memory issues
3. **Indexing**: Email indexed for fast lookups
4. **Connection Validation**: pool_pre_ping=True for stale connection handling

## Security Considerations

1. **Password Security**: Bcrypt with salt rounds=12
2. **JWT Expiration**: Tokens expire after 30 minutes
3. **CORS Configuration**: Allowed from all origins (update for production)
4. **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
5. **Input Validation**: Pydantic validates all inputs
6. **HTTPS**: Use in production

## Deployment

### Production Checklist

- [ ] Change `SECRET_KEY` to a strong random string
- [ ] Set `DEBUG=False`
- [ ] Set `ENVIRONMENT=production`
- [ ] Update CORS origins
- [ ] Configure production database
- [ ] Set up proper logging
- [ ] Enable HTTPS
- [ ] Configure SSL certificates
- [ ] Set up monitoring and alerts
- [ ] Configure backup strategy

### Docker Deployment

```bash
# Build image
docker build -t food-delivery-api:1.0.0 .

# Run container
docker run -d \
  --name food-delivery-api \
  -p 8000:8000 \
  -e DATABASE_URL=mysql://... \
  -e SECRET_KEY=... \
  food-delivery-api:1.0.0
```

## Troubleshooting

### Database Connection Issues
```bash
# Test MySQL connection
mysql -u root -p -h localhost

# Check MySQL service
sudo service mysql status
```

### JWT Token Errors
- Ensure `SECRET_KEY` is set correctly
- Check token expiration time
- Verify Authorization header format

### Port Already in Use
```bash
# Linux/Mac: Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/name`
4. Create Pull Request

## Roadmap

- [ ] Rate limiting
- [ ] Email notifications
- [ ] SMS notifications
- [ ] Real-time order tracking
- [ ] Advanced analytics
- [ ] Stripe integration
- [ ] Google Maps integration
- [ ] Mobile app API
- [ ] GraphQL API
- [ ] WebSocket support for live updates

## Support

For issues and questions:
1. Check existing issues
2. Create detailed issue report
3. Provide error logs and steps to reproduce

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Contact

- Email: support@fooddelivery.com
- Website: www.fooddelivery.com
- Documentation: docs.fooddelivery.com

---

**Made with ❤️ by Food Delivery Team**
