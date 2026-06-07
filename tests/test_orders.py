"""API tests for order endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import get_auth_headers


def test_create_order(client: TestClient, test_customer_user, test_restaurant, test_menu_item):
    """Test creating an order."""
    headers = get_auth_headers(test_customer_user)
    
    response = client.post(
        "/orders",
        headers=headers,
        json={
            "restaurant_id": test_restaurant.id,
            "delivery_address": "789 Order Street",
            "items": [
                {
                    "menu_item_id": test_menu_item.id,
                    "quantity": 2
                }
            ]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == test_customer_user.id
    assert data["total_amount"] == 99.99 * 2


def test_create_order_invalid_restaurant(client: TestClient, test_customer_user):
    """Test creating order with invalid restaurant."""
    headers = get_auth_headers(test_customer_user)
    
    response = client.post(
        "/orders",
        headers=headers,
        json={
            "restaurant_id": 9999,
            "delivery_address": "789 Order Street",
            "items": [
                {
                    "menu_item_id": 1,
                    "quantity": 1
                }
            ]
        }
    )
    
    assert response.status_code == 404


def test_create_order_empty_items(client: TestClient, test_customer_user, test_restaurant):
    """Test creating order with no items."""
    headers = get_auth_headers(test_customer_user)
    
    response = client.post(
        "/orders",
        headers=headers,
        json={
            "restaurant_id": test_restaurant.id,
            "delivery_address": "789 Order Street",
            "items": []
        }
    )
    
    assert response.status_code == 422


def test_list_orders_customer(client: TestClient, test_customer_user, test_order):
    """Test listing orders as customer."""
    headers = get_auth_headers(test_customer_user)
    
    response = client.get("/orders", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_get_order(client: TestClient, test_customer_user, test_order):
    """Test getting order details."""
    headers = get_auth_headers(test_customer_user)
    
    response = client.get(f"/orders/{test_order.id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_order.id


def test_get_order_forbidden(client: TestClient, db: Session):
    """Test getting order of another user (forbidden)."""
    from app.models import User, Order, OrderStatus
    from app.auth import PasswordManager
    
    # Create two different customers
    customer1 = User(
        name="Customer 1",
        email="customer1@example.com",
        phone="9876543220",
        password_hash=PasswordManager.hash_password("Pass123!"),
        role="customer"
    )
    customer2 = User(
        name="Customer 2",
        email="customer2@example.com",
        phone="9876543221",
        password_hash=PasswordManager.hash_password("Pass123!"),
        role="customer"
    )
    db.add(customer1)
    db.add(customer2)
    db.flush()
    
    # Create restaurant and order for customer1
    from app.models import Restaurant, OrderStatus
    restaurant = Restaurant(
        owner_id=customer1.id,
        restaurant_name="Test",
        address="Test",
        city="Test",
        phone="1234567890",
        is_active=True
    )
    db.add(restaurant)
    db.flush()
    
    order = Order(
        user_id=customer1.id,
        restaurant_id=restaurant.id,
        total_amount=100,
        delivery_address="Test",
        order_status=OrderStatus.PENDING
    )
    db.add(order)
    db.commit()
    
    # Try to access order as customer2
    headers = get_auth_headers(customer2)
    response = client.get(f"/orders/{order.id}", headers=headers)
    
    assert response.status_code == 403


def test_update_order_status(client: TestClient, test_restaurant_owner, test_order):
    """Test updating order status."""
    headers = get_auth_headers(test_restaurant_owner)
    
    from app.models import OrderStatus
    response = client.put(
        f"/orders/{test_order.id}",
        headers=headers,
        json={
            "order_status": OrderStatus.PREPARING.value
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["order_status"] == OrderStatus.PREPARING.value


def test_cancel_order_customer(client: TestClient, test_customer_user, test_order):
    """Test customer cancelling their order."""
    headers = get_auth_headers(test_customer_user)
    
    from app.models import OrderStatus
    response = client.put(
        f"/orders/{test_order.id}",
        headers=headers,
        json={
            "order_status": OrderStatus.CANCELLED.value
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["order_status"] == OrderStatus.CANCELLED.value
