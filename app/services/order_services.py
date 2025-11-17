"""
Order service - Business logic for order operations
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
import uuid

from app.models.models import Order
from app.schemas.schema import OrderCreate, OrderUpdate

logger = logging.getLogger(__name__)


class OrderService:
    """Service for order operations"""

    @staticmethod
    def get_all_orders(db: Session, user_id: Optional[int] = None) -> List[Order]:
        """Get all orders, optionally filtered by user"""
        try:
            query = db.query(Order)
            if user_id:
                query = query.filter(Order.user_id == user_id)
            orders = query.all()
            logger.info(f"Retrieved {len(orders)} orders")
            return orders
        except Exception as e:
            logger.error(f"Error retrieving orders: {str(e)}")
            raise

    @staticmethod
    def get_order_by_id(db: Session, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                logger.info(f"Retrieved order: {order_id}")
            return order
        except Exception as e:
            logger.error(f"Error retrieving order {order_id}: {str(e)}")
            raise

    @staticmethod
    def create_order(db: Session, order_data: OrderCreate, user_id: int) -> Order:
        """Create new order"""
        try:
            order_id = f"ORD{uuid.uuid4().hex[:8].upper()}"
            
            new_order = Order(
                id=order_id,
                **order_data.dict(),
                user_id=user_id
            )
            db.add(new_order)
            db.commit()
            db.refresh(new_order)
            logger.info(f"Created order: {order_id} for user: {user_id}")
            return new_order
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating order: {str(e)}")
            raise

    @staticmethod
    def update_order(db: Session, order_id: str, order_data: OrderUpdate) -> Optional[Order]:
        """Update order"""
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                logger.warning(f"Order not found: {order_id}")
                return None
            
            update_data = order_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(order, key, value)
            
            db.commit()
            db.refresh(order)
            logger.info(f"Updated order: {order_id}")
            return order
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating order {order_id}: {str(e)}")
            raise

    @staticmethod
    def cancel_order(db: Session, order_id: str) -> Optional[Order]:
        """Cancel order"""
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                logger.warning(f"Order not found: {order_id}")
                return None
            
            if order.status == "COMPLETED":
                logger.warning(f"Cannot cancel completed order: {order_id}")
                return None
            
            order.status = "CANCELLED"
            db.commit()
            db.refresh(order)
            logger.info(f"Cancelled order: {order_id}")
            return order
        except Exception as e:
            db.rollback()
            logger.error(f"Error cancelling order {order_id}: {str(e)}")
            raise

    @staticmethod
    def delete_order(db: Session, order_id: str) -> bool:
        """Delete order (only pending orders)"""
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                logger.warning(f"Order not found: {order_id}")
                return False
            
            if order.status != "PENDING":
                logger.warning(f"Cannot delete non-pending order: {order_id}")
                return False
            
            db.delete(order)
            db.commit()
            logger.info(f"Deleted order: {order_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting order {order_id}: {str(e)}")
            raise

    @staticmethod
    def execute_order(db: Session, order_id: str, executed_price: float, executed_qty: int) -> Optional[Order]:
        """Execute/fill order"""
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return None
            
            order.status = "COMPLETED"
            order.executed_price = executed_price
            order.executed_qty = executed_qty
            
            db.commit()
            db.refresh(order)
            logger.info(f"Executed order: {order_id} - {executed_qty} @ {executed_price}")
            return order
        except Exception as e:
            db.rollback()
            logger.error(f"Error executing order {order_id}: {str(e)}")
            raise
