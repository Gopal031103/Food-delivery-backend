"""API tests for restaurant endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import get_auth_headers


def test_create_restaurant(client: TestClient, test_restaurant_owner):
    """Test restaurant creation."""
    headers = get_auth_headers(test_restaurant_owner)
    
    response = client.post(
        "/restaurants",
        headers=headers,
        json={
            "restaurant_name": "New Restaurant",
            "address": "789 New Street",
            "city": "New City",
            "phone": "9876543216",
            "email": "newrestaurant@example.com"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["restaurant_name"] == "New Restaurant"


def test_list_restaurants(client: TestClient, test_restaurant):
    """Test listing restaurants."""
    response = client.get("/restaurants")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_get_restaurant(client: TestClient, test_restaurant):
    """Test getting restaurant details."""
    response = client.get(f"/restaurants/{test_restaurant.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_restaurant.id


def test_update_restaurant(client: TestClient, test_restaurant_owner, test_restaurant):
    """Test updating restaurant."""
    headers = get_auth_headers(test_restaurant_owner)
    
    response = client.put(
        f"/restaurants/{test_restaurant.id}",
        headers=headers,
        json={
            "restaurant_name": "Updated Restaurant Name"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["restaurant_name"] == "Updated Restaurant Name"


def test_update_restaurant_forbidden(
    client: TestClient,
    test_customer_user,
    test_restaurant
):
    """Test updating restaurant as non-owner (forbidden)."""
    headers = get_auth_headers(test_customer_user)
    
    response = client.put(
        f"/restaurants/{test_restaurant.id}",
        headers=headers,
        json={
            "restaurant_name": "Hacked Name"
        }
    )
    
    assert response.status_code == 403


def test_delete_restaurant(client: TestClient, test_restaurant_owner, test_restaurant):
    """Test deleting restaurant."""
    headers = get_auth_headers(test_restaurant_owner)
    
    response = client.delete(
        f"/restaurants/{test_restaurant.id}",
        headers=headers
    )
    
    assert response.status_code == 204


def test_activate_restaurant(client: TestClient, test_admin_user, test_restaurant):
    """Test activating restaurant (admin only)."""
    headers = get_auth_headers(test_admin_user)
    
    response = client.put(
        f"/restaurants/{test_restaurant.id}/activate",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == True


def test_deactivate_restaurant(client: TestClient, test_admin_user, test_restaurant):
    """Test deactivating restaurant (admin only)."""
    headers = get_auth_headers(test_admin_user)
    
    response = client.put(
        f"/restaurants/{test_restaurant.id}/deactivate",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == False
