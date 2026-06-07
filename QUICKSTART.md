# Quick Start Guide

Get the Food Delivery Management System up and running in minutes!

## Prerequisites

- Python 3.13
- MySQL 8.0+
- Git
- Optional: Docker & Docker Compose

## Option 1: Quick Setup (Local)

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd "Food App delivery  Project"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure Database

```bash
# Create MySQL database
mysql -u root -p

# In MySQL:
CREATE DATABASE food_delivery;
EXIT;
```

### Step 3: Configure Environment

```bash
# Copy example .env file
cp .env.example .env

# Edit .env with your MySQL credentials
# Set DATABASE_URL=mysql+mysqlconnector://root:your_password@localhost:3306/food_delivery
```

### Step 4: Run Application

```bash
# Start the API server
uvicorn app.main:app --reload --port 8000
```

### Step 5: Access API

- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

## Option 2: Docker Setup (Recommended)

### Step 1: Build and Run

```bash
# Navigate to project directory
cd "Food App delivery  Project"

# Build and run with Docker Compose
docker-compose up --build
```

### Step 2: Wait for Services

The MySQL database will initialize automatically. Wait for the message:
```
food_delivery_app | Application startup complete
```

### Step 3: Access Services

- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/api/docs
- **MySQL**: localhost:3306

### Stop Services

```bash
docker-compose down
```

## Testing the API

### 1. Register a Customer

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210",
    "password": "SecurePass123!"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

Copy the `access_token` from response.

### 3. Get Current User

```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Using Postman

1. Import the Postman collection: `Food_Delivery_API.postman_collection.json`
2. Set variables:
   - `base_url`: http://localhost:8000
   - `token`: Your JWT token from login
3. Start testing endpoints

## Running Tests

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app tests/

# Verbose output
pytest -v
```

## Common Tasks

### Create Admin User

```python
from app.auth import PasswordManager
from app.database import SessionLocal
from app.models import User, UserRole

db = SessionLocal()

admin = User(
    name="Admin",
    email="admin@example.com",
    phone="9999999999",
    password_hash=PasswordManager.hash_password("AdminPass123!"),
    role=UserRole.ADMIN
)

db.add(admin)
db.commit()
print(f"Admin created: {admin.email}")
```

### Create Restaurant Owner

```python
from app.auth import PasswordManager
from app.database import SessionLocal
from app.models import User, UserRole

db = SessionLocal()

owner = User(
    name="Restaurant Owner",
    email="owner@example.com",
    phone="9999999998",
    password_hash=PasswordManager.hash_password("OwnerPass123!"),
    role=UserRole.RESTAURANT_OWNER
)

db.add(owner)
db.commit()
print(f"Owner created: {owner.email}")
```

### Query Database Directly

```python
from app.database import SessionLocal
from app.models import User

db = SessionLocal()

# Get all users
users = db.query(User).all()
for user in users:
    print(f"{user.id}: {user.email} ({user.role})")

db.close()
```

## Debugging

### Enable Debug Mode

Edit `.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### Check Logs

```bash
# View application logs (if running with --reload)
# Logs appear in console

# Docker logs
docker logs food_delivery_app
```

### Database Connection Test

```python
from app.database import engine

try:
    with engine.connect() as conn:
        print("✓ Database connected")
except Exception as e:
    print(f"✗ Database error: {e}")
```

## Troubleshooting

### Port 8000 Already in Use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID YOUR_PID /F

# Linux/Mac
lsof -i :8000
kill -9 YOUR_PID
```

### MySQL Connection Failed

1. Verify MySQL is running: `mysql -u root -p`
2. Check DATABASE_URL in .env
3. Verify database exists: `SHOW DATABASES;`

### Virtual Environment Issues

```bash
# Remove and recreate venv
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Docker Issues

```bash
# Remove old containers
docker-compose down -v

# Rebuild
docker-compose up --build

# View logs
docker-compose logs -f app
```

## API Workflow Example

### Customer Order Flow

1. **Register** → Get user account
2. **Login** → Get JWT token
3. **Browse Restaurants** → See available restaurants
4. **View Menu** → See restaurant menu items
5. **Create Order** → Place order with items
6. **Make Payment** → Process payment
7. **Track Order** → Monitor order status

### Restaurant Owner Flow

1. **Register as Owner** → Create account
2. **Create Restaurant** → Add restaurant details
3. **Add Menu Items** → Create menu
4. **Receive Orders** → Get customer orders
5. **Update Order Status** → Prepare and deliver

## Next Steps

1. Read full [README.md](README.md) for comprehensive documentation
2. Check [DATABASE_SETUP.md](DATABASE_SETUP.md) for database details
3. Explore API endpoints in Swagger: http://localhost:8000/api/docs
4. Review test files for usage examples
5. Deploy to production (see Deployment section in README)

## Support

- **Documentation**: See README.md
- **API Docs**: Swagger UI at /api/docs
- **Tests**: Run `pytest -v` for test details
- **Issues**: Check troubleshooting section

## Quick Reference

| Task | Command |
|------|---------|
| Start Dev Server | `uvicorn app.main:app --reload` |
| Run Tests | `pytest -v` |
| Docker Start | `docker-compose up` |
| Docker Stop | `docker-compose down` |
| Create DB | `mysql -u root -p < schema.sql` |
| Access Docs | http://localhost:8000/api/docs |

## Architecture Overview

```
┌─────────────────────────────────────┐
│   Client (Web/Mobile/Postman)      │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│   FastAPI Application (Port 8000)   │
│  ├─ Authentication Routes           │
│  ├─ User Management Routes          │
│  ├─ Restaurant Routes               │
│  ├─ Menu Routes                     │
│  ├─ Order Routes                    │
│  └─ Payment Routes                  │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│   SQLAlchemy ORM                    │
│   (Database Layer)                  │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│   MySQL Database (Port 3306)        │
│   ├─ users                          │
│   ├─ restaurants                    │
│   ├─ menu_items                     │
│   ├─ orders                         │
│   ├─ order_items                    │
│   └─ payments                       │
└─────────────────────────────────────┘
```

---

**Ready to go!** 🚀 Start with the API and enjoy building!
