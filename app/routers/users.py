"""User management routes."""
import logging
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.schemas import UserResponse, UserUpdate, AdminUserResponse
from app.auth import get_current_user, get_current_admin_user
from app.exceptions import ResourceNotFoundException, ForbiddenException
from app.utils import PaginationUtils

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[AdminUserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> list[AdminUserResponse]:
    """
    Get all users (Admin only).
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    skip, limit = PaginationUtils.get_pagination_params(skip, limit)
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Get user details.
    
    Users can only view their own profile unless they are admin.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise ResourceNotFoundException(detail=f"User with ID {user_id} not found")
    
    # Check permissions
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise ForbiddenException(detail="You can only view your own profile")
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Update user profile.
    
    Users can only update their own profile unless they are admin.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise ResourceNotFoundException(detail=f"User with ID {user_id} not found")
    
    # Check permissions
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise ForbiddenException(detail="You can only update your own profile")
    
    # Update fields
    if user_update.name:
        user.name = user_update.name
    if user_update.phone:
        user.phone = user_update.phone
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"User {user_id} profile updated")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete user (Admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise ResourceNotFoundException(detail=f"User with ID {user_id} not found")
    
    db.delete(user)
    db.commit()
    
    logger.info(f"User {user_id} deleted by admin")


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current logged-in user's profile."""
    return current_user
