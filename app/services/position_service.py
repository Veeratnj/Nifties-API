"""
Position service - Business logic for position/live trades operations
"""

import logging
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi import Request
from app.models.models import Order, Strategy
from app.schemas.schema import OrderCreate, OrderUpdate # Replaced PositionCreate/Update with Order ones or kept these if needed for imports elsewhere

logger = logging.getLogger(__name__)


class PositionService:
    """Service for position operations"""

    @staticmethod
    def get_all_positions(db: Session, ltp_data: dict = {}, user_id: Optional[int] = None, user_role: str = "USER") -> List[dict]:
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
            query = db.query(Order).options(
                joinedload(Order.strategy),
                joinedload(Order.signal_log)
            ).filter(
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
            return [PositionService._transform_order_to_position(o, ltp_data) for o in orders]
        except Exception as e:
            logger.error(f"Error retrieving open trades: {str(e)}")
            raise

    @staticmethod
    def _transform_order_to_position(order: Order, ltp_data: dict = {}) -> dict:
        """Transform Order model to frontend expected format for positions with PnL calculation"""
        
        # P&L calculation
        entry_price = float(order.entry_price or 0)
        qty = int(order.qty or 0)
        
        # Determine token for LTP
        token = None
        side = "BUY" # Default side
        
        if order.signal_log:
            token = order.signal_log.token
            side = order.signal_log.signal_type # Assuming signal_type contains SIDE like BUY_ENTRY, SELL_ENTRY
        
        # Get Current Price based on status
        current_price = 0.0
        if order.status.upper() == "CLOSED":
            current_price = float(order.exit_price or 0)
        else:
            # For OPEN or other statuses, use LTP
            if token and ltp_data:
                current_price = float(ltp_data.get(str(token), 0) or 0)
        
        # If Current Price is 0 (LTP not available or missing exit price), use entry price as fallback for display (but keep PnL 0)
        display_current_price = current_price if current_price > 0 else entry_price
        
        # Calculate PnL based on side
        pnl = 0.0
        pnl_percent = 0.0
        
        if current_price > 0 and entry_price > 0 and qty > 0:
            if "BUY" in side.upper():
                pnl = (current_price - entry_price) * qty
            elif "SELL" in side.upper():
                pnl = (entry_price - current_price) * qty
            
            pnl_percent = (pnl / (entry_price * qty)) * 100 if entry_price > 0 else 0
        
        # Get strategy name
        strategy_name = None
        if order.strategy:
            strategy_name = order.strategy.name
        
        return {
            "id": order.id,
            "user_id": order.user_id,
            "symbol": order.symbol,
            "index": getattr(order, "underlying", "NIFTY"), 
            "strike": 0, 
            "type": order.option_type,
            "qty": qty,
            "entry_price": entry_price,
            "current_price": display_current_price,
            "pnl": round(pnl, 2),
            "pnl_percent": round(pnl_percent, 2),
            "status": order.status,
            "strategy": strategy_name,
            "timestamp": order.entry_time,
            "created_at": order.entry_time,
            "updated_at": order.entry_time
        }

    @staticmethod
    def get_active_positions(db: Session, ltp_data: dict = {}, user_id: int = None) -> List[dict]:
        """Get active/open trades for user from Order table (Today only)"""
        try:
            today = date.today()
            query = db.query(Order).options(
                joinedload(Order.strategy),
                joinedload(Order.signal_log)
            ).filter(
                (Order.exit_price == None) | (Order.exit_price == 0),
                Order.is_deleted == False,
                func.date(Order.entry_time) == today
            )

            if user_id:
                query = query.filter(Order.user_id == user_id)
            
            orders = query.all()
            
            logger.info(f"Retrieved {len(orders)} active trades for user: {user_id}")
            return [PositionService._transform_order_to_position(o, ltp_data) for o in orders]
        except Exception as e:
            logger.error(f"Error retrieving active trades: {str(e)}")
            raise

    @staticmethod
    def get_position_by_id(db: Session, position_id: int, ltp_data: dict = {}) -> Optional[dict]:
        """Get trade by ID from Order table, formatted for frontend"""
        try:
            order = db.query(Order).options(
                joinedload(Order.strategy),
                joinedload(Order.signal_log)
            ).filter(
                Order.id == position_id
            ).first()
            
            if order:
                logger.info(f"Retrieved trade: {position_id}")
                return PositionService._transform_order_to_position(order, ltp_data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving trade {position_id}: {str(e)}")
            raise
