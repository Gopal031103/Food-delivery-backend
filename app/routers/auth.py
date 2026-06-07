"""Authentication routes."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.schemas import TokenRequest, TokenResponse, UserCreate, UserResponse
from app.models import User, UserRole
from app.auth import PasswordManager, JWTManager
from app.exceptions import (
    ValidationException,
    DuplicateResourceException,
    UnauthorizedException
)
from app.config import settings
from app.utils import ValidationUtils

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)) -> User:
    """
    Register a new user.
    
    - **name**: User's full name (min 2 characters)
    - **email**: User's email address (must be unique)
    - **phone**: User's phone number
    - **password**: User's password (min 8 characters with uppercase, digit, special char)
    """
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise DuplicateResourceException(
                detail=f"Email {user_data.email} is already registered"
            )
        
        # Validate phone
        if not ValidationUtils.validate_phone(user_data.phone):
            raise ValidationException(detail="Invalid phone number format")
        
        # Hash password
        password_hash = PasswordManager.hash_password(user_data.password)
        
        # Create new user
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=password_hash,
            role=user_data.role
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user registered: {new_user.email}")
        return new_user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during registration: {str(e)}")
        raise


@router.post("/login", response_model=TokenResponse)
async def login(credentials: TokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Login with email and password.
    
    Returns JWT access token for subsequent API calls.
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user:
            raise UnauthorizedException(
                detail="Invalid email or password"
            )
        
        # Verify password
        if not PasswordManager.verify_password(credentials.password, user.password_hash):
            raise UnauthorizedException(
                detail="Invalid email or password"
            )
        
        # Create JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value
        }
        access_token = JWTManager.create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise
