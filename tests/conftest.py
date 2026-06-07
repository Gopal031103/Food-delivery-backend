"""Test fixtures and configuration."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.database import get_db, Base
from app.models import User, Restaurant, MenuItem, Order, OrderItem, UserRole, OrderStatus
from app.auth import PasswordManager, JWTManager


# Use in-memory SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database and session."""
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield db_session
    
    db_session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_customer_user(db: Session) -> User:
    """Create test customer user."""
    user = User(
        name="Test Customer",
        email="customer@example.com",
        phone="9876543210",
        password_hash=PasswordManager.hash_password("TestPass123!"),
        role=UserRole.CUSTOMER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_restaurant_owner(db: Session) -> User:
    """Create test restaurant owner user."""
    user = User(
        name="Test Owner",
        email="owner@example.com",
        phone="9876543211",
        password_hash=PasswordManager.hash_password("OwnerPass123!"),
        role=UserRole.RESTAURANT_OWNER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db: Session) -> User:
    """Create test admin user."""
    user = User(
        name="Test Admin",
        email="admin@example.com",
        phone="9876543212",
        password_hash=PasswordManager.hash_password("AdminPass123!"),
        role=UserRole.ADMIN
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_restaurant(db: Session, test_restaurant_owner: User) -> Restaurant:
    """Create test restaurant."""
    restaurant = Restaurant(
        owner_id=test_restaurant_owner.id,
        restaurant_name="Test Restaurant",
        address="123 Main St",
        city="Test City",
        phone="9876543210",
        email="restaurant@example.com",
        is_active=True
    )
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


@pytest.fixture
def test_menu_item(db: Session, test_restaurant: Restaurant) -> MenuItem:
    """Create test menu item."""
    item = MenuItem(
        restaurant_id=test_restaurant.id,
        food_name="Test Burger",
        description="Delicious test burger",
        category="Main Course",
        price=99.99,
        available=True
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@pytest.fixture
def test_order(db: Session, test_customer_user: User, test_restaurant: Restaurant) -> Order:
    """Create test order."""
    order = Order(
        user_id=test_customer_user.id,
        restaurant_id=test_restaurant.id,
        total_amount=99.99,
        delivery_address="456 Test Ave",
        order_status=OrderStatus.PENDING
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_token(user: User) -> str:
    """Generate JWT token for user."""
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value
    }
    token = JWTManager.create_access_token(token_data)
    return token


def get_auth_headers(user: User) -> dict:
    """Get authorization headers with JWT token."""
    token = get_token(user)
    return {"Authorization": f"Bearer {token}"}
