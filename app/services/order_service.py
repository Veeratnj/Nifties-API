"""
Order service - Business logic for order operations with field transformation
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models.models import Order, Strategy,Position
from app.schemas.schema import OrderCreate, OrderUpdate

logger = logging.getLogger(__name__)


class OrderService:
    """Service for order operations"""

    @staticmethod
    def get_all_orders(db: Session, user_id: Optional[int] = None, user_role: str = "USER") -> List[dict]:
        """
        Get EXECUTED orders based on user role:
        - SUPERADMIN/ADMIN: Get ALL executed orders from all users
        - USER/TRADER: Get only their own executed orders
        """
        try:
            query = db.query(Order).options(
                joinedload(Order.strategy),
                joinedload(Order.position)  # Join with Position to get exit price
            )
            
            # Filter to only EXECUTED orders
            query = query.filter(Order.status == "EXECUTED")
            
            # Role-based filtering
            if user_role in ["SUPERADMIN", "ADMIN"]:
                # Admins see all executed orders
                logger.info(f"Admin user accessing all executed orders")
            else:
                # Regular users see only their executed orders
                if user_id:
                    query = query.filter(Order.user_id == user_id)
                    logger.info(f"User {user_id} accessing their executed orders")
            
            orders = query.all()
            logger.info(f"Retrieved {len(orders)} executed orders")
            
            # Transform to frontend format
            return [OrderService._transform_order(o) for o in orders]
        except Exception as e:
            logger.error(f"Error retrieving orders: {str(e)}")
            raise

    @staticmethod
    def _transform_order(order: Order) -> dict:
        """Transform Order model to frontend expected format"""
        # Get strategy name
        strategy_name = None
        if order.strategy:
            strategy_name = order.strategy.name
        
        # Calculate total price (qty × per unit price)
        unit_price = float(order.price) if order.price else 0.0
        total_price = order.qty * unit_price
        
        # Handle EXECUTED orders - set execution details
        executed_qty = order.executed_qty or 0
        avg_exec_price = float(order.avg_executed_price) if order.avg_executed_price else None
        executed_at = order.executed_at
        
        if order.status.value == "EXECUTED":
            # If marked as EXECUTED but fields are empty, use order values
            if executed_qty == 0:
                executed_qty = order.qty  # Full qty was executed
            
            # Get exit price from Position table's current_price
            # First try the linked position
            position = order.position
            print(f"[DEBUG] Order {order.id} - Linked position: {position}")
            
            # If no linked position, try to find position by symbol and user_id
            if not position and order._sa_instance_state.session:
                position = order._sa_instance_state.session.query(Position).filter(
                    Position.symbol == order.symbol,
                    Position.user_id == order.user_id
                ).first()
                print(f"[DEBUG] Order {order.id} - Lookup position by symbol={order.symbol}, user_id={order.user_id}: {position}")
            
            # Get exit price from position's current_price
            if position:
                print(f"[DEBUG] Order {order.id} - Position found! current_price={position.avg_exit_price}")
                if position.avg_exit_price:
                    avg_exec_price = float(position.avg_exit_price)  # Exit price from Position
                    print(f"[DEBUG] Order {order.id} - Set avg_exec_price to {avg_exec_price}")
            else:
                print(f"[DEBUG] Order {order.id} - NO Position found!")
            
            if avg_exec_price is None:
                avg_exec_price = unit_price  # Fallback to order price
                print(f"[DEBUG] Order {order.id} - Using fallback price: {avg_exec_price}")
            
            if executed_at is None:
                executed_at = order.placed_at  # Use placed_at as fallback
        
        return {
            "id": order.id,
            "user_id": order.user_id,
            "strategy_id": order.strategy_id,
            "position_id": order.position_id,
            "symbol": order.symbol,
            "underlying": order.underlying,
            "order_type": order.order_type.value,  # Convert enum to string
            "product_type": order.product_type,
            "qty": order.qty,
            "price": total_price,  # Total order value (qty × unit price)
            "avg_price": unit_price,  # Entry price per unit/stock
            "trigger_price": float(order.trigger_price) if order.trigger_price else None,
            "status": order.status.value,  # Convert enum to string
            
            # Internal tracking
            "order_id": order.order_id,
            
            # Execution details - properly set for EXECUTED orders
            "executed_qty": executed_qty,
            "pending_qty": order.pending_qty if order.status.value != "EXECUTED" else 0,
            "cancelled_qty": order.cancelled_qty or 0,
            "avg_executed_price": avg_exec_price,  # Exit price from Position's current_price
            "exit_price": avg_exec_price,  # Also add as exit_price field
            
            # Broker details
            "broker_order_id": order.broker_order_id,
            "exchange_order_id": order.exchange_order_id,
            "exchange": order.exchange,
            "rejection_reason": order.rejection_reason,
            "status_message": order.status_message,
            
            # Timestamps - map placed_at to both timestamp and created_at
            "timestamp": order.placed_at,
            "placed_at": order.placed_at,
            "executed_at": executed_at,
            "updated_at": order.updated_at or order.placed_at,
            "created_at": order.placed_at  # Map placed_at to created_at
        }

    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> Optional[dict]:
        """Get order by ID, formatted for frontend"""
        try:
            order = db.query(Order).options(joinedload(Order.strategy)).filter(
                Order.id == order_id
            ).first()
            
            if order:
                logger.info(f"Retrieved order: {order_id}")
                return OrderService._transform_order(order)
            return None
        except Exception as e:
            logger.error(f"Error retrieving order {order_id}: {str(e)}")
            raise
