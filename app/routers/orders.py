"""Order management routes."""
import logging
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    User, Order, OrderItem, MenuItem, Restaurant, 
    UserRole, OrderStatus
)
from app.schemas import OrderCreate, OrderResponse, OrderUpdate, OrderItemResponse
from app.auth import (
    get_current_user,
    get_current_customer,
    get_current_restaurant_owner,
    get_current_admin_user
)
from app.exceptions import (
    ResourceNotFoundException,
    ForbiddenException,
    ValidationException
)
from app.utils import PaginationUtils

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Order:
    """
    Create a new order.
    
    Only customers can create orders.
    """
    # Verify restaurant exists
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == order_data.restaurant_id,
        Restaurant.is_active == True
    ).first()
    
    if not restaurant:
        raise ResourceNotFoundException(
            detail=f"Restaurant with ID {order_data.restaurant_id} not found"
        )
    
    if not order_data.items:
        raise ValidationException(detail="Order must contain at least one item")
    
    # Calculate total and validate items
    total_amount = 0
    order_items = []
    
    for item_data in order_data.items:
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == item_data.menu_item_id,
            MenuItem.restaurant_id == order_data.restaurant_id,
            MenuItem.available == True
        ).first()
        
        if not menu_item:
            raise ResourceNotFoundException(
                detail=f"Menu item with ID {item_data.menu_item_id} not found"
            )
        
        item_total = menu_item.price * item_data.quantity
        total_amount += item_total
        
        order_items.append({
            "menu_item": menu_item,
            "quantity": item_data.quantity,
            "item_price": menu_item.price
        })
    
    # Create order
    new_order = Order(
        user_id=current_user.id,
        restaurant_id=order_data.restaurant_id,
        total_amount=total_amount,
        delivery_address=order_data.delivery_address,
        order_status=OrderStatus.PENDING
    )
    
    db.add(new_order)
    db.flush()
    
    # Add order items
    for item_info in order_items:
        order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=item_info["menu_item"].id,
            quantity=item_info["quantity"],
            item_price=item_info["item_price"]
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(new_order)
    
    logger.info(f"Order created: {new_order.id} by user {current_user.id}")
    return new_order


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: OrderStatus = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[OrderResponse]:
    """
    Get orders based on user role.
    
    - Customers see their own orders
    - Restaurant owners see orders for their restaurants
    - Admins see all orders
    """
    skip, limit = PaginationUtils.get_pagination_params(skip, limit)
    
    query = db.query(Order)
    
    if current_user.role == UserRole.CUSTOMER:
        query = query.filter(Order.user_id == current_user.id)
    elif current_user.role == UserRole.RESTAURANT_OWNER:
        restaurants = db.query(Restaurant).filter(
            Restaurant.owner_id == current_user.id
        ).all()
        restaurant_ids = [r.id for r in restaurants]
        query = query.filter(Order.restaurant_id.in_(restaurant_ids))
    # Admin sees all orders (no filter)
    
    if status_filter:
        query = query.filter(Order.order_status == status_filter)
    
    orders = query.offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Order:
    """Get order details."""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise ResourceNotFoundException(
            detail=f"Order with ID {order_id} not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.CUSTOMER:
        if order.user_id != current_user.id:
            raise ForbiddenException(detail="You can only view your own orders")
    elif current_user.role == UserRole.RESTAURANT_OWNER:
        restaurant = db.query(Restaurant).filter(
            Restaurant.id == order.restaurant_id
        ).first()
        if restaurant.owner_id != current_user.id:
            raise ForbiddenException(
                detail="You can only view orders for your own restaurant"
            )
    
    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Order:
    """
    Update order status.
    
    - Customers can cancel pending orders
    - Restaurant owners can update order status
    - Admins can update order status
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise ResourceNotFoundException(
            detail=f"Order with ID {order_id} not found"
        )
    
    # Permission checks
    if current_user.role == UserRole.CUSTOMER:
        if order.user_id != current_user.id:
            raise ForbiddenException(detail="You can only cancel your own orders")
        if order_update.order_status != OrderStatus.CANCELLED:
            raise ForbiddenException(
                detail="Customers can only cancel orders"
            )
        if order.order_status != OrderStatus.PENDING:
            raise ValidationException(
                detail="Only pending orders can be cancelled"
            )
    elif current_user.role == UserRole.RESTAURANT_OWNER:
        restaurant = db.query(Restaurant).filter(
            Restaurant.id == order.restaurant_id
        ).first()
        if restaurant.owner_id != current_user.id:
            raise ForbiddenException(
                detail="You can only update orders for your own restaurant"
            )
    
    order.order_status = order_update.order_status
    db.commit()
    db.refresh(order)
    
    logger.info(f"Order {order_id} status updated to {order_update.order_status}")
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> None:
    """Delete order (Admin only)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise ResourceNotFoundException(
            detail=f"Order with ID {order_id} not found"
        )
    
    db.delete(order)
    db.commit()
    
    logger.info(f"Order {order_id} deleted by admin")
