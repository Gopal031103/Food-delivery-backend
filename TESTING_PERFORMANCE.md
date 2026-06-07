# Testing & Performance Guide

Comprehensive guide for testing and optimizing the Food Delivery Management System.

## Unit Testing

### Test Structure

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── test_auth.py         # Authentication tests
├── test_restaurants.py  # Restaurant endpoint tests
├── test_orders.py       # Order endpoint tests
├── test_menu.py         # Menu endpoint tests
└── test_payments.py     # Payment endpoint tests
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_register_user

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app tests/

# Run with specific marker
pytest -m "not slow"

# Run tests in parallel
pytest -n auto
```

### Test Fixtures

```python
# tests/conftest.py provides fixtures:
- db: Database session for testing
- client: FastAPI test client
- test_customer_user: Pre-created customer
- test_restaurant_owner: Pre-created restaurant owner
- test_admin_user: Pre-created admin
- test_restaurant: Pre-created restaurant
- test_menu_item: Pre-created menu item
- test_order: Pre-created order
```

### Writing Tests

```python
import pytest
from fastapi.testclient import TestClient

def test_create_order(client: TestClient, test_customer_user, test_restaurant, test_menu_item):
    """Test order creation."""
    headers = get_auth_headers(test_customer_user)
    
    response = client.post(
        "/orders",
        headers=headers,
        json={
            "restaurant_id": test_restaurant.id,
            "delivery_address": "789 Test St",
            "items": [{"menu_item_id": test_menu_item.id, "quantity": 2}]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["total_amount"] == test_menu_item.price * 2
    assert data["order_status"] == "pending"
```

### Test Coverage

Target coverage:
- **Overall**: > 80%
- **Routes**: > 90%
- **Models**: > 85%
- **Utils**: > 75%

```bash
# Generate coverage report
pytest --cov=app --cov-report=html tests/

# View HTML report
open htmlcov/index.html
```

## API Testing

### Load Testing with Locust

```python
# locustfile.py
from locust import HttpUser, task, between
import random

class FoodDeliveryUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def list_restaurants(self):
        self.client.get("/restaurants", headers=self.headers)
    
    @task(2)
    def list_orders(self):
        self.client.get("/orders", headers=self.headers)
    
    @task(1)
    def create_order(self):
        self.client.post("/orders", headers=self.headers, json={
            "restaurant_id": random.randint(1, 5),
            "delivery_address": "Test Address",
            "items": [{"menu_item_id": 1, "quantity": 1}]
        })
```

Run load test:
```bash
# Install locust
pip install locust

# Run load test
locust -f locustfile.py --host=http://localhost:8000 -u 100 -r 10 -t 60s
```

### API Testing with Postman

1. Import `Food_Delivery_API.postman_collection.json`
2. Configure variables:
   - `base_url`: http://localhost:8000
   - `token`: Your JWT token
3. Use Postman's Collection Runner for batch testing
4. Configure Tests tab for assertions:

```javascript
// Example test assertion
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has correct structure", function () {
    let jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('email');
});
```

### Integration Testing

```python
# tests/test_integration.py
def test_complete_order_flow(client, db):
    """Test complete order workflow."""
    # 1. Register customer
    customer_response = client.post("/auth/register", json={
        "name": "Test Customer",
        "email": f"customer{random.randint(1, 9999)}@example.com",
        "phone": "9876543210",
        "password": "TestPass123!"
    })
    assert customer_response.status_code == 201
    
    # 2. Login
    login_response = client.post("/auth/login", json={
        "email": customer_response.json()["email"],
        "password": "TestPass123!"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create order
    order_response = client.post("/orders", headers=headers, json={
        "restaurant_id": 1,
        "delivery_address": "Test Address",
        "items": [{"menu_item_id": 1, "quantity": 1}]
    })
    assert order_response.status_code == 201
    order_id = order_response.json()["id"]
    
    # 4. Create payment
    payment_response = client.post("/payments", headers=headers, json={
        "order_id": order_id,
        "payment_method": "credit_card"
    })
    assert payment_response.status_code == 201
    
    # 5. Verify order status updated
    order_response = client.get(f"/orders/{order_id}", headers=headers)
    assert order_response.json()["order_status"] == "confirmed"
```

## Performance Testing

### Database Query Performance

```python
# tests/test_performance.py
import time

def test_list_restaurants_performance(client):
    """Test restaurant listing performance."""
    start = time.time()
    
    response = client.get("/restaurants?limit=100")
    
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 0.5  # Should respond in < 500ms
```

### Database Optimization

```python
# Query optimization example
def get_restaurant_with_items(restaurant_id: int, db: Session):
    """
    Optimized query using joinedload to prevent N+1 problem.
    """
    from sqlalchemy.orm import joinedload
    
    restaurant = db.query(Restaurant)\
        .options(joinedload(Restaurant.menu_items))\
        .filter(Restaurant.id == restaurant_id)\
        .first()
    
    return restaurant
```

### Response Time Profiling

```python
# Add middleware for response time tracking
from time import time
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    
    logger.info(f"{request.method} {request.url.path} - {process_time:.3f}s")
    response.headers["X-Process-Time"] = str(process_time)
    
    return response
```

### Memory Profiling

```bash
# Install memory_profiler
pip install memory-profiler

# Run with memory profiling
python -m memory_profiler app/main.py
```

## Performance Benchmarks

Expected performance metrics:

| Endpoint | Method | P50 | P95 | P99 |
|----------|--------|-----|-----|-----|
| /health | GET | 5ms | 10ms | 20ms |
| /restaurants | GET | 50ms | 100ms | 150ms |
| /orders | POST | 100ms | 200ms | 300ms |
| /orders | GET | 80ms | 150ms | 250ms |
| /auth/login | POST | 200ms | 400ms | 600ms |
| /auth/register | POST | 300ms | 500ms | 800ms |

## Stress Testing

### Apache JMeter Configuration

1. Create Test Plan
2. Add Thread Group (100 threads)
3. Add HTTP Samplers for each endpoint
4. Add Listeners (View Results Tree, Aggregate Report)
5. Run and analyze results

### k6 Load Testing

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp-up
    { duration: '1m30s', target: 100 },
    { duration: '20s', target: 0 },    // Ramp-down
  ],
};

export default function () {
  // Test endpoints
  let getRes = http.get('http://localhost:8000/restaurants');
  check(getRes, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
}
```

Run k6 test:
```bash
k6 run load-test.js
```

## Debugging

### Enable Debug Logging

```python
# app/main.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Request: {request.method} {request.url.path}")
    logger.debug(f"Headers: {request.headers}")
    response = await call_next(request)
    logger.debug(f"Response status: {response.status_code}")
    return response
```

### Query Debugging

```python
# Enable SQL query logging
from sqlalchemy import event
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Or with execution time tracking
event.listen(Engine, "before_cursor_execute", 
    lambda conn, cursor, statement, parameters, context, executemany: 
        print(f"Query: {statement}\nParams: {parameters}"))
```

### Breakpoint Debugging

```python
# Add breakpoint in code
@app.get("/debug-endpoint")
async def debug_endpoint():
    breakpoint()  # Execution will pause here
    return {"message": "debug"}
```

Run with debugger:
```bash
python -m pdb app/main.py
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test and Build

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: food_delivery
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
        ports:
          - 3306:3306
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.13'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: pytest --cov=app tests/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Best Practices

1. **Test Organization**
   - Group related tests in files
   - Use descriptive test names
   - One assertion per test when possible

2. **Performance**
   - Monitor response times in production
   - Set performance budgets
   - Profile regularly

3. **Security**
   - Test authentication flows
   - Test authorization checks
   - Test input validation

4. **Database**
   - Monitor query performance
   - Use connection pooling
   - Regular index optimization

5. **Monitoring**
   - Track error rates
   - Monitor resource usage
   - Set up alerts for anomalies
