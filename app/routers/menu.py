"""Menu management routes."""
import logging
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, MenuItem, Restaurant, UserRole
from app.schemas import MenuItemCreate, MenuItemResponse, MenuItemUpdate
from app.auth import get_current_user, get_current_admin_user
from app.exceptions import (
    ResourceNotFoundException,
    ForbiddenException,
    ValidationException
)
from app.utils import PaginationUtils

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/menu", tags=["Menu"])


@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    menu_item_data: MenuItemCreate,
    restaurant_id: int = Query(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MenuItem:
    """
    Create a new menu item.
    
    Only restaurant owner can add items to their menu.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if not restaurant:
        raise ResourceNotFoundException(
            detail=f"Restaurant with ID {restaurant_id} not found"
        )
    
    # Check permissions
    if current_user.id != restaurant.owner_id:
        raise ForbiddenException(
            detail="You can only add items to your own restaurant menu"
        )
    
    new_item = MenuItem(
        restaurant_id=restaurant_id,
        food_name=menu_item_data.food_name,
        description=menu_item_data.description,
        category=menu_item_data.category,
        price=menu_item_data.price,
        available=True
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    logger.info(f"Menu item created: {new_item.food_name} in restaurant {restaurant_id}")
    return new_item


@router.get("", response_model=list[MenuItemResponse])
async def list_menu_items(
    restaurant_id: int = Query(..., gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: str = Query(None),
    db: Session = Depends(get_db)
) -> list[MenuItemResponse]:
    """
    Get menu items for a restaurant.
    
    - **restaurant_id**: ID of the restaurant
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **category**: Filter by category (optional)
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if not restaurant:
        raise ResourceNotFoundException(
            detail=f"Restaurant with ID {restaurant_id} not found"
        )
    
    skip, limit = PaginationUtils.get_pagination_params(skip, limit)
    
    query = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id,
        MenuItem.available == True
    )
    
    if category:
        query = query.filter(MenuItem.category.ilike(f"%{category}%"))
    
    items = query.offset(skip).limit(limit).all()
    return items


@router.get("/{menu_item_id}", response_model=MenuItemResponse)
async def get_menu_item(
    menu_item_id: int,
    db: Session = Depends(get_db)
) -> MenuItem:
    """Get menu item details."""
    item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    
    if not item:
        raise ResourceNotFoundException(
            detail=f"Menu item with ID {menu_item_id} not found"
        )
    
    if not item.available:
        raise ResourceNotFoundException(
            detail="This menu item is not available"
        )
    
    return item


@router.put("/{menu_item_id}", response_model=MenuItemResponse)
async def update_menu_item(
    menu_item_id: int,
    item_update: MenuItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MenuItem:
    """
    Update menu item.
    
    Only restaurant owner can update their menu items.
    """
    item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    
    if not item:
        raise ResourceNotFoundException(
            detail=f"Menu item with ID {menu_item_id} not found"
        )
    
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == item.restaurant_id
    ).first()
    
    # Check permissions
    if current_user.id != restaurant.owner_id:
        raise ForbiddenException(
            detail="You can only update items in your own restaurant menu"
        )
    
    # Update fields
    if item_update.food_name:
        item.food_name = item_update.food_name
    if item_update.description:
        item.description = item_update.description
    if item_update.category:
        item.category = item_update.category
    if item_update.price:
        item.price = item_update.price
    if item_update.available is not None:
        item.available = item_update.available
    
    db.commit()
    db.refresh(item)
    
    logger.info(f"Menu item {menu_item_id} updated")
    return item


@router.delete("/{menu_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(
    menu_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete menu item.
    
    Only restaurant owner can delete their menu items.
    """
    item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    
    if not item:
        raise ResourceNotFoundException(
            detail=f"Menu item with ID {menu_item_id} not found"
        )
    
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == item.restaurant_id
    ).first()
    
    # Check permissions
    if current_user.id != restaurant.owner_id:
        raise ForbiddenException(
            detail="You can only delete items from your own restaurant menu"
        )
    
    db.delete(item)
    db.commit()
    
    logger.info(f"Menu item {menu_item_id} deleted")
