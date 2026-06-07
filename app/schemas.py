"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models import UserRole, OrderStatus, PaymentStatus, PaymentMethod


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    role: Optional[UserRole] = UserRole.CUSTOMER


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=255)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)


# Authentication Schemas
class TokenRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Schema for decoded JWT token data."""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None


# Restaurant Schemas
class RestaurantBase(BaseModel):
    """Base restaurant schema."""
    restaurant_name: str = Field(..., min_length=3, max_length=255)
    address: str = Field(..., min_length=5, max_length=500)
    city: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None


class RestaurantCreate(RestaurantBase):
    """Schema for creating restaurant."""
    pass


class RestaurantUpdate(BaseModel):
    """Schema for updating restaurant."""
    restaurant_name: Optional[str] = Field(None, min_length=3, max_length=255)
    address: Optional[str] = Field(None, min_length=5, max_length=500)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None


class RestaurantResponse(RestaurantBase):
    """Schema for restaurant response."""
    id: int
    owner_id: int
    rating: float
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# MenuItem Schemas
class MenuItemBase(BaseModel):
    """Base menu item schema."""
    food_name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0)


class MenuItemCreate(MenuItemBase):
    """Schema for creating menu item."""
    pass


class MenuItemUpdate(BaseModel):
    """Schema for updating menu item."""
    food_name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    available: Optional[bool] = None


class MenuItemResponse(MenuItemBase):
    """Schema for menu item response."""
    id: int
    restaurant_id: int
    available: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Order Schemas
class OrderItemCreate(BaseModel):
    """Schema for adding items to order."""
    menu_item_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    """Schema for creating order."""
    restaurant_id: int
    delivery_address: str = Field(..., min_length=5, max_length=500)
    items: List[OrderItemCreate] = Field(..., min_items=1)


class OrderItemResponse(BaseModel):
    """Schema for order item response."""
    id: int
    order_id: int
    menu_item_id: int
    quantity: int
    item_price: float
    
    class Config:
        from_attributes = True


class OrderUpdate(BaseModel):
    """Schema for updating order status (admin only)."""
    order_status: OrderStatus


class OrderResponse(BaseModel):
    """Schema for order response."""
    id: int
    user_id: int
    restaurant_id: int
    total_amount: float
    order_status: OrderStatus
    delivery_address: str
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Payment Schemas
class PaymentCreate(BaseModel):
    """Schema for creating payment."""
    order_id: int
    payment_method: PaymentMethod


class PaymentResponse(BaseModel):
    """Schema for payment response."""
    id: int
    order_id: int
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    transaction_id: Optional[str]
    amount: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Admin Schemas
class AdminUserResponse(BaseModel):
    """Schema for admin to view user details."""
    id: int
    name: str
    email: str
    phone: str
    role: UserRole
    created_at: datetime
    
    class Config:
        from_attributes = True


# Error Response
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
    status_code: int
    timestamp: Optional[datetime] = None
