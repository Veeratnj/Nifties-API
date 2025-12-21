"""
Position service - Business logic for position/live trades operations
"""

import logging
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.models import Order, Strategy
from app.schemas.schema import OrderCreate, OrderUpdate # Replaced PositionCreate/Update with Order ones or kept these if needed for imports elsewhere

logger = logging.getLogger(__name__)


class PositionService:
    """Service for position operations"""

    @staticmethod
    def get_all_positions(db: Session, user_id: Optional[int] = None, user_role: str = "USER") -> List[dict]:
        """
        Get open trades from Order table based on user role:
        - SUPERADMIN/ADMIN: Get ALL open trades from all users
        - USER/TRADER: Get only their own open trades
        """
        try:
            today = date.today()
            # We filter for orders where exit_price is None or 0 (indicating they are still open)
            # and status is EXECUTED or PLACED
            # ADDED: Filtering by entry_time to show only today's trades
            query = db.query(Order).options(joinedload(Order.strategy)).filter(
                (Order.exit_price == None) | (Order.exit_price == 0),
                Order.is_deleted == False,
                func.date(Order.entry_time) == today
            )
            
            # Role-based filtering
            if user_role in ["SUPERADMIN", "ADMIN"]:
                logger.info(f"Admin user accessing all open trades")
            else:
                if user_id:
                    query = query.filter(Order.user_id == user_id)
                    logger.info(f"User {user_id} accessing their open trades")
                else:
                    # If no user_id and not admin, return empty list for security
                    logger.warning("No user_id provided for non-admin user")
                    return []
            
            orders = query.all()
            logger.info(f"Retrieved {len(orders)} open trades from orders table")
            
            # Transform to frontend format
            return [PositionService._transform_order_to_position(o) for o in orders]
        except Exception as e:
            logger.error(f"Error retrieving open trades: {str(e)}")
            raise

    @staticmethod
    def _transform_order_to_position(order: Order) -> dict:
        """Transform Order model to frontend expected format for positions"""
        # P&L calculation (mock/placeholder as orders might not have live P&L)
        # In a real scenario, this might fetch LTP and calculate
        pnl = 0.0
        pnl_percent = 0.0
        
        # Get strategy name
        strategy_name = None
        if order.strategy:
            strategy_name = order.strategy.name
        
        # Status mapping for frontend
        status = "ACTIVE"
        
        return {
            "id": order.id,
            "user_id": order.user_id,
            "symbol": order.symbol,
            "index": getattr(order, "underlying", "NIFTY"),  # Safeguard if field missing
            "strike": 0, # Placeholder if not in Order model
            "type": order.option_type,
            "qty": order.qty,
            "entry_price": float(order.entry_price or 0),
            "current_price": float(order.entry_price or 0), # Default to entry if live price not available
            "pnl": pnl,
            "pnl_percent": pnl_percent,
            "status": status,
            "strategy": strategy_name,
            "timestamp": order.entry_time,
            "created_at": order.entry_time,
            "updated_at": order.entry_time
        }

    @staticmethod
    def get_active_positions(db: Session, user_id: int) -> List[dict]:
        """Get active/open trades for user from Order table (Today only)"""
        try:
            today = date.today()
            orders = db.query(Order).options(joinedload(Order.strategy)).filter(
                Order.user_id == user_id,
                (Order.exit_price == None) | (Order.exit_price == 0),
                Order.is_deleted == False,
                func.date(Order.entry_time) == today
            ).all()
            
            logger.info(f"Retrieved {len(orders)} active trades for user: {user_id}")
            return [PositionService._transform_order_to_position(o) for o in orders]
        except Exception as e:
            logger.error(f"Error retrieving active trades: {str(e)}")
            raise

    @staticmethod
    def get_position_by_id(db: Session, position_id: int) -> Optional[dict]:
        """Get trade by ID from Order table, formatted for frontend"""
        try:
            order = db.query(Order).options(joinedload(Order.strategy)).filter(
                Order.id == position_id
            ).first()
            
            if order:
                logger.info(f"Retrieved trade: {position_id}")
                return PositionService._transform_order_to_position(order)
            return None
        except Exception as e:
            logger.error(f"Error retrieving trade {position_id}: {str(e)}")
            raise
