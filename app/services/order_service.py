"""
Order service - Business logic for order operations with field transformation
"""

import logging
from typing import List, Optional
from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.models import Order, Strategy # Removed Position import
from app.schemas.schema import OrderCreate, OrderUpdate

logger = logging.getLogger(__name__)


class OrderService:
    """Service for order operations"""

    @staticmethod
    def get_all_orders(db: Session, user_id: Optional[int] = None, user_role: str = "USER") -> List[dict]:
        """
        Get CLOSED orders based on user role:
        - SUPERADMIN/ADMIN: Get ALL closed orders from all users
        - USER/TRADER: Get only their own closed orders
        """
        try:
            query = db.query(Order).options(joinedload(Order.strategy)).filter(Order.status == "CLOSED")
            
            # Role-based filtering
            if user_role not in ["ADMIN", "SUPERADMIN"]:
                if user_id:
                    query = query.filter(Order.user_id == user_id)
                else:
                    return [] # Security check
            
            orders = query.all()
            logger.info(f"Retrieved {len(orders)} closed orders")
            
            # Transform to frontend format
            return [OrderService._transform_order(o) for o in orders]
        except Exception as e:
            logger.error(f"Error retrieving orders: {str(e)}")
            raise

    @staticmethod
    def _transform_order(order: Order) -> dict:
        """Transform Order model to frontend expected format with defensive mapping"""
        # Get strategy name
        strategy_name = None
        if order.strategy:
            strategy_name = order.strategy.name
        
        # Mapping correct field names from Model (entry_price, qty)
        unit_price = float(order.entry_price) if order.entry_price else 0.0
        total_price = order.qty * unit_price
        
        # Handle execution details defensively
        executed_qty = getattr(order, 'executed_qty', order.qty)
        avg_exec_price = float(order.exit_price) if order.exit_price else unit_price
        executed_at = getattr(order, 'executed_at', order.exit_time or order.entry_time)
        
        # Calculate P&L and P&L percent
        entry_p = float(order.entry_price or 0)
        exit_p = float(order.exit_price or 0)
        pnl = (exit_p - entry_p) * order.qty
        pnl_percent = ((exit_p - entry_p) / entry_p * 100) if entry_p > 0 else 0
        
        return {
            "id": order.id,
            "user_id": order.user_id,
            "strategy_id": order.strategy_id,
            "position_id": getattr(order, 'position_id', None),
            "symbol": order.symbol,
            "underlying": getattr(order, 'underlying', getattr(order.strategy, 'underlying', 'NIFTY')),
            "order_type": order.option_type, # Using option_type (CE/PE)
            "product_type": getattr(order, 'product_type', 'NRML'),
            "qty": order.qty,
            "price": total_price,  # Total value
            "avg_price": unit_price,  # Entry price
            "exit_price": avg_exec_price,
            "pnl": round(pnl, 2),
            "pnl_percent": round(pnl_percent, 2),
            "trigger_price": float(getattr(order, 'trigger_price', 0)) or None,
            "status": order.status,
            
            # Internal tracking
            "order_id": getattr(order, 'order_id', str(order.id)),
            
            # Execution details
            "executed_qty": executed_qty,
            "pending_qty": getattr(order, 'pending_qty', 0),
            "cancelled_qty": getattr(order, 'cancelled_qty', 0),
            "avg_executed_price": avg_exec_price,
            
            # Broker/Exchange details
            "broker_order_id": getattr(order, 'broker_order_id', None),
            "exchange_order_id": getattr(order, 'exchange_order_id', None),
            "exchange": getattr(order, 'exchange', 'NSE'),
            "rejection_reason": getattr(order, 'rejection_reason', None),
            "status_message": getattr(order, 'status_message', None),
            
            # Timestamps
            "timestamp": order.entry_time,
            "placed_at": order.entry_time,
            "executed_at": executed_at,
            "updated_at": getattr(order, 'updated_at', order.entry_time),
            "created_at": order.entry_time
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
