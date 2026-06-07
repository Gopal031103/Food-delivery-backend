"""Payment management routes."""
import logging
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Payment, Order, PaymentStatus, OrderStatus, UserRole
from app.schemas import PaymentCreate, PaymentResponse
from app.auth import (
    get_current_user,
    get_current_admin_user
)
from app.exceptions import (
    ResourceNotFoundException,
    ForbiddenException,
    ValidationException,
    DuplicateResourceException
)
from app.utils import PaginationUtils

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Payment:
    """
    Create payment for an order.
    
    Only the order owner can create payment.
    """
    order = db.query(Order).filter(Order.id == payment_data.order_id).first()
    
    if not order:
        raise ResourceNotFoundException(
            detail=f"Order with ID {payment_data.order_id} not found"
        )
    
    # Check permissions
    if order.user_id != current_user.id:
        raise ForbiddenException(
            detail="You can only create payment for your own orders"
        )
    
    # Check if payment already exists
    existing_payment = db.query(Payment).filter(
        Payment.order_id == payment_data.order_id
    ).first()
    
    if existing_payment:
        if existing_payment.payment_status == PaymentStatus.COMPLETED:
            raise ValidationException(
                detail="Payment for this order is already completed"
            )
        raise DuplicateResourceException(
            detail="Payment for this order already exists"
        )
    
    # Check order status
    if order.order_status in [OrderStatus.CANCELLED, OrderStatus.DELIVERED]:
        raise ValidationException(
            detail=f"Cannot create payment for {order.order_status} order"
        )
    
    # Create payment
    new_payment = Payment(
        order_id=payment_data.order_id,
        payment_method=payment_data.payment_method,
        payment_status=PaymentStatus.PENDING,
        amount=order.total_amount,
        transaction_id=f"TXN-{order.id}-{current_user.id}"
    )
    
    db.add(new_payment)
    
    # Update order status
    order.order_status = OrderStatus.CONFIRMED
    
    db.commit()
    db.refresh(new_payment)
    
    logger.info(f"Payment created for order {payment_data.order_id}")
    return new_payment


@router.get("", response_model=list[PaymentResponse])
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: PaymentStatus = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[PaymentResponse]:
    """
    Get payments based on user role.
    
    - Customers see payments for their orders
    - Restaurant owners see payments for their restaurant orders
    - Admins see all payments
    """
    skip, limit = PaginationUtils.get_pagination_params(skip, limit)
    
    query = db.query(Payment)
    
    if current_user.role == UserRole.CUSTOMER:
        # Customers see payments for their own orders
        query = query.join(Order).filter(Order.user_id == current_user.id)
    elif current_user.role == UserRole.RESTAURANT_OWNER:
        # Restaurant owners see payments for their restaurant orders
        query = query.join(Order).filter(
            Order.restaurant_id.in_(
                db.query(User).filter(User.id == current_user.id)
                .first().restaurants if current_user else []
            )
        )
    
    if status_filter:
        query = query.filter(Payment.payment_status == status_filter)
    
    payments = query.offset(skip).limit(limit).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Payment:
    """Get payment details."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise ResourceNotFoundException(
            detail=f"Payment with ID {payment_id} not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.CUSTOMER:
        if payment.order.user_id != current_user.id:
            raise ForbiddenException(
                detail="You can only view payments for your own orders"
            )
    elif current_user.role == UserRole.RESTAURANT_OWNER:
        if payment.order.restaurant_id not in [r.id for r in current_user.restaurants]:
            raise ForbiddenException(
                detail="You can only view payments for your restaurant orders"
            )
    
    return payment


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment_status(
    payment_id: int,
    status: PaymentStatus,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Payment:
    """
    Update payment status (Admin only).
    
    Used to mark payments as completed or failed.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise ResourceNotFoundException(
            detail=f"Payment with ID {payment_id} not found"
        )
    
    payment.payment_status = status
    
    # Update order status based on payment status
    if status == PaymentStatus.COMPLETED:
        payment.order.order_status = OrderStatus.PREPARING
    elif status == PaymentStatus.FAILED:
        payment.order.order_status = OrderStatus.PENDING
    elif status == PaymentStatus.REFUNDED:
        payment.order.order_status = OrderStatus.CANCELLED
    
    db.commit()
    db.refresh(payment)
    
    logger.info(f"Payment {payment_id} status updated to {status}")
    return payment
