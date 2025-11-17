"""
Order controller - Order management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.db import get_db
from app.schemas.schema import OrderSchema, OrderCreate, OrderUpdate, ResponseSchema
from app.services.order_services import OrderService
from app.models.models import User
from app.utils.security import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=ResponseSchema[List[OrderSchema]])
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders for current user"""
    try:
        orders = OrderService.get_all_orders(db, user_id=current_user.id)
        return ResponseSchema(data=orders, message="Orders retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving orders"
        )


@router.get("/{order_id}", response_model=ResponseSchema[OrderSchema])
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific order"""
    order = OrderService.get_order_by_id(db, order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if not (order.user_id == current_user.id or current_user.role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order"
        )
    
    return ResponseSchema(data=order)


@router.post("", response_model=ResponseSchema[OrderSchema], status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new order"""
    try:
        new_order = OrderService.create_order(db, order_data, current_user.id)
        logger.info(f"Order created for user {current_user.id}: {new_order.id}")
        return ResponseSchema(
            data=new_order,
            status=201,
            message="Order created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating order"
        )


@router.put("/{order_id}", response_model=ResponseSchema[OrderSchema])
async def update_order(
    order_id: str,
    order_data: OrderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update order"""
    order = OrderService.get_order_by_id(db, order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if not (order.user_id == current_user.id or current_user.role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this order"
        )
    
    try:
        updated_order = OrderService.update_order(db, order_id, order_data)
        return ResponseSchema(data=updated_order, message="Order updated successfully")
    except Exception as e:
        logger.error(f"Error updating order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating order"
        )


@router.patch("/{order_id}/cancel", response_model=ResponseSchema[OrderSchema])
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel order"""
    order = OrderService.get_order_by_id(db, order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if not (order.user_id == current_user.id or current_user.role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this order"
        )
    
    try:
        cancelled_order = OrderService.cancel_order(db, order_id)
        if not cancelled_order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel this order"
            )
        return ResponseSchema(data=cancelled_order, message="Order cancelled successfully")
    except Exception as e:
        logger.error(f"Error cancelling order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cancelling order"
        )


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete order"""
    order = OrderService.get_order_by_id(db, order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if not (order.user_id == current_user.id or current_user.role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this order"
        )
    
    deleted = OrderService.delete_order(db, order_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete this order"
        )
    
    return None
