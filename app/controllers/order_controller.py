"""
Order controller - Order management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.db import get_db
from app.schemas.schema import OrderSchema, OrderCreate, OrderUpdate, ResponseSchema
from app.services.order_service import OrderService
from app.models.models import User
from app.utils.security import get_current_user

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=ResponseSchema)
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get orders based on user role:
    - SUPERADMIN/ADMIN: See ALL users' orders
    - USER/TRADER: See only their own orders
    """
    try:
        print('qwe1234')
        # Pass user role for access control
        orders = OrderService.get_all_orders(
            db, 
            user_id=current_user.id,
            user_role=current_user.role.value
        )
        return ResponseSchema(data=orders, message="Orders retrieved successfully")
    except Exception as e:
        print("error is ",e)
        logger.error(f"Error getting orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving orders"
        )


@router.get("/{order_id}", response_model=ResponseSchema)
async def get_order(
    order_id: int,
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
    
    if not (order["user_id"] == current_user.id or current_user.role.value in ["ADMIN", "SUPERADMIN"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order"
        )
    
    return ResponseSchema(data=order)
