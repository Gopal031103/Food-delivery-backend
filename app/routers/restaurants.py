"""Restaurant management routes."""
import logging
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Restaurant, UserRole
from app.schemas import RestaurantCreate, RestaurantResponse, RestaurantUpdate
from app.auth import get_current_user, get_current_restaurant_owner, get_current_admin_user
from app.exceptions import (
    ResourceNotFoundException,
    ForbiddenException,
    ValidationException
)
from app.utils import PaginationUtils

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.post("", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant_data: RestaurantCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Restaurant:
    """
    Create a new restaurant.
    
    Only restaurant owners can create restaurants.
    """
    # Change user role to restaurant owner
    if current_user.role != UserRole.RESTAURANT_OWNER:
        current_user.role = UserRole.RESTAURANT_OWNER
        db.commit()
    
    new_restaurant = Restaurant(
        owner_id=current_user.id,
        restaurant_name=restaurant_data.restaurant_name,
        address=restaurant_data.address,
        city=restaurant_data.city,
        phone=restaurant_data.phone,
        email=restaurant_data.email
    )
    
    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)
    
    logger.info(f"Restaurant created: {new_restaurant.restaurant_name} by user {current_user.id}")
    return new_restaurant


@router.get("", response_model=list[RestaurantResponse])
async def list_restaurants(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    city: str = Query(None),
    db: Session = Depends(get_db)
) -> list[RestaurantResponse]:
    """
    Get all restaurants.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **city**: Filter by city (optional)
    """
    skip, limit = PaginationUtils.get_pagination_params(skip, limit)
    
    query = db.query(Restaurant).filter(Restaurant.is_active == True)
    
    if city:
        query = query.filter(Restaurant.city.ilike(f"%{city}%"))
    
    restaurants = query.offset(skip).limit(limit).all()
    return restaurants


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db)
) -> Restaurant:
    """Get restaurant details."""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if not restaurant:
        raise ResourceNotFoundException(
            detail=f"Restaurant with ID {restaurant_id} not found"
        )
    
    if not restaurant.is_active:
        raise ResourceNotFoundException(
            detail="This restaurant is currently inactive"
        )
    
    return restaurant


@router.put("/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(
    restaurant_id: int,
    restaurant_update: RestaurantUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Restaurant:
    """
    Update restaurant details.
    
    Only restaurant owner or admin can update.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if not restaurant:
        raise ResourceNotFoundException(
            detail=f"Restaurant with ID {restaurant_id} not found"
        )
    
    # Check permissions
    if (current_user.id != restaurant.owner_id and 
        current_user.role != UserRole.ADMIN):
        raise ForbiddenException(
            detail="You can only update your own restaurant"
        )
    
    # Update fields
    if restaurant_update.restaurant_name:
        restaurant.restaurant_name = restaurant_update.restaurant_name
    if restaurant_update.address:
        restaurant.address = restaurant_update.address
    if restaurant_update.city:
        restaurant.city = restaurant_update.city
    if restaurant_update.phone:
        restaurant.phone = restaurant_update.phone
    if restaurant_update.email:
        restaurant.email = restaurant_update.email
    
    db.commit()
    db.refresh(restaurant)
    
    logger.info(f"Restaurant {restaurant_id} updated")
    return restaurant


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant(
    restaurant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete restaurant.
    
    Only owner or admin can delete.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if not restaurant:
        raise ResourceNotFoundException(
            detail=f"Restaurant with ID {restaurant_id} not found"
        )
    
    # Check permissions
    if (current_user.id != restaurant.owner_id and 
        current_user.role != UserRole.ADMIN):
        raise ForbiddenException(
            detail="You can only delete your own restaurant"
        )
    
    db.delete(restaurant)
    db.commit()
    
    logger.info(f"Restaurant {restaurant_id} deleted")


@router.put("/{restaurant_id}/activate", response_model=RestaurantResponse)
async def activate_restaurant(
    restaurant_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Restaurant:
    """Activate restaurant (Admin only)."""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if not restaurant:
        raise ResourceNotFoundException(
            detail=f"Restaurant with ID {restaurant_id} not found"
        )
    
    restaurant.is_active = True
    db.commit()
    db.refresh(restaurant)
    
    logger.info(f"Restaurant {restaurant_id} activated by admin")
    return restaurant


@router.put("/{restaurant_id}/deactivate", response_model=RestaurantResponse)
async def deactivate_restaurant(
    restaurant_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Restaurant:
    """Deactivate restaurant (Admin only)."""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if not restaurant:
        raise ResourceNotFoundException(
            detail=f"Restaurant with ID {restaurant_id} not found"
        )
    
    restaurant.is_active = False
    db.commit()
    db.refresh(restaurant)
    
    logger.info(f"Restaurant {restaurant_id} deactivated by admin")
    return restaurant
