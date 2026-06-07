"""API tests for authentication endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import get_auth_headers


def test_register_user(client: TestClient, db: Session):
    """Test user registration."""
    response = client.post(
        "/auth/register",
        json={
            "name": "New User",
            "email": "newuser@example.com",
            "phone": "9876543213",
            "password": "NewPass123!"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "customer"


def test_register_user_duplicate_email(client: TestClient, db: Session, test_customer_user):
    """Test registration with duplicate email."""
    response = client.post(
        "/auth/register",
        json={
            "name": "Another User",
            "email": test_customer_user.email,
            "phone": "9876543214",
            "password": "AnotherPass123!"
        }
    )
    
    assert response.status_code == 409


def test_register_user_weak_password(client: TestClient, db: Session):
    """Test registration with weak password."""
    response = client.post(
        "/auth/register",
        json={
            "name": "User",
            "email": "user@example.com",
            "phone": "9876543215",
            "password": "weak"
        }
    )
    
    assert response.status_code == 422


def test_login_success(client: TestClient, db: Session, test_customer_user):
    """Test successful login."""
    response = client.post(
        "/auth/login",
        json={
            "email": test_customer_user.email,
            "password": "TestPass123!"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_email(client: TestClient, db: Session):
    """Test login with invalid email."""
    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "AnyPass123!"
        }
    )
    
    assert response.status_code == 401


def test_login_invalid_password(client: TestClient, db: Session, test_customer_user):
    """Test login with invalid password."""
    response = client.post(
        "/auth/login",
        json={
            "email": test_customer_user.email,
            "password": "WrongPass123!"
        }
    )
    
    assert response.status_code == 401


def test_get_current_user(client: TestClient, test_customer_user):
    """Test getting current user profile."""
    headers = get_auth_headers(test_customer_user)
    
    response = client.get("/users/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_customer_user.email


def test_get_current_user_without_token(client: TestClient):
    """Test getting current user without token."""
    response = client.get("/users/me")
    
    assert response.status_code == 403


def test_get_user_profile(client: TestClient, test_customer_user):
    """Test getting user profile."""
    headers = get_auth_headers(test_customer_user)
    
    response = client.get(
        f"/users/{test_customer_user.id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_customer_user.id


def test_update_user_profile(client: TestClient, test_customer_user):
    """Test updating user profile."""
    headers = get_auth_headers(test_customer_user)
    
    response = client.put(
        f"/users/{test_customer_user.id}",
        headers=headers,
        json={
            "name": "Updated Name",
            "phone": "1234567890"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"


def test_list_users_admin_only(client: TestClient, test_admin_user, test_customer_user):
    """Test listing users (admin only)."""
    headers = get_auth_headers(test_admin_user)
    
    response = client.get("/users", headers=headers)
    
    assert response.status_code == 200


def test_list_users_customer_forbidden(client: TestClient, test_customer_user):
    """Test listing users as customer (forbidden)."""
    headers = get_auth_headers(test_customer_user)
    
    response = client.get("/users", headers=headers)
    
    assert response.status_code == 403
