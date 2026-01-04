"""
Position service - Business logic for position/live trades operations
"""

import logging
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi import Request
from app.models.models import Order, Strategy, StrikePriceTickData, SignalLog
from sqlalchemy import desc, func, outerjoin

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
            
            # Subquery to get the latest LTP for each symbol
            latest_ltp_subquery = db.query(
                StrikePriceTickData.symbol,
                func.max(StrikePriceTickData.id).label('max_id')
            ).group_by(StrikePriceTickData.symbol).subquery()

            ltp_join = db.query(
                StrikePriceTickData.symbol,
                StrikePriceTickData.ltp
            ).join(
                latest_ltp_subquery,
                StrikePriceTickData.id == latest_ltp_subquery.c.max_id
            ).subquery()

            # We filter for orders where exit_price is None or 0 (indicating they are still open)
            # if order is open we can in our order table  status is OPEN if it is closed then status is CLOSED
            # and status is EXECUTED or PLACED
            query = db.query(Order, ltp_join.c.ltp.label('current_ltp')).outerjoin(
                ltp_join, Order.symbol == ltp_join.c.symbol
            ).options(
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
                    logger.warning("No user_id provided for non-admin user")
                    return []
            
            results = query.all()
            logger.info(f"Retrieved {len(results)} open trades from orders table")
            
            # Transform to frontend format
            return [PositionService._transform_order_to_position(row.Order, row.current_ltp) for row in results]
        except Exception as e:
            logger.error(f"Error retrieving open trades: {str(e)}")
            raise

    @staticmethod
    def _transform_order_to_position(order: Order, current_ltp: Optional[float] = None) -> dict:
        """Transform Order model to frontend expected format for positions with PnL calculation"""
        
        # P&L calculation
        entry_price = float(order.entry_price or 0)
        qty = int(order.qty or 0)
        
        # Determine side
        side = "BUY"
        if order.signal_log:
            side = order.signal_log.signal_type
        
        # Get Current Price based on status
        current_price = 0.0
        if order.status.upper() == "CLOSED":
            current_price = float(order.exit_price or 0)
        else:
            # Use pre-fetched LTP from DB join
            current_price = float(current_ltp or 0)
        
        # Fallback for display
        display_current_price = current_price if current_price > 0 else entry_price
        
        # Calculate PnL
        pnl = 0.0
        pnl_percent = 0.0
        
        if current_price > 0 and entry_price > 0 and qty > 0:
            if "BUY" in side.upper():
                pnl = (current_price - entry_price) * qty
            elif "SELL" in side.upper():
                pnl = (entry_price - current_price) * qty
            
            pnl_percent = (pnl / (entry_price * qty)) * 100 if entry_price > 0 else 0
        
        # Get strategy name
        strategy_name = order.strategy.name if order.strategy else None
        
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
    def get_active_positions(db: Session, user_id: int = None) -> List[dict]:
        """Get active/open trades for user from Order table (Today only)"""
        try:
            today = date.today()
            
            # Subquery logic repeated for consistent joins
            latest_ltp_subquery = db.query(
                StrikePriceTickData.symbol,
                func.max(StrikePriceTickData.id).label('max_id')
            ).group_by(StrikePriceTickData.symbol).subquery()

            ltp_join = db.query(
                StrikePriceTickData.symbol,
                StrikePriceTickData.ltp
            ).join(
                latest_ltp_subquery,
                StrikePriceTickData.id == latest_ltp_subquery.c.max_id
            ).subquery()

            query = db.query(Order, ltp_join.c.ltp.label('current_ltp')).outerjoin(
                ltp_join, Order.symbol == ltp_join.c.symbol
            ).options(
                joinedload(Order.strategy),
                joinedload(Order.signal_log)
            ).filter(
                (Order.exit_price == None) | (Order.exit_price == 0),
                Order.is_deleted == False,
                func.date(Order.entry_time) == today
            )

            if user_id:
                query = query.filter(Order.user_id == user_id)
            
            results = query.all()
            
            logger.info(f"Retrieved {len(results)} active trades for user: {user_id}")
            return [PositionService._transform_order_to_position(row.Order, row.current_ltp) for row in results]
        except Exception as e:
            logger.error(f"Error retrieving active trades: {str(e)}")
            raise

    @staticmethod
    def get_position_by_id(db: Session, position_id: int) -> Optional[dict]:
        """Get trade by ID from Order table, formatted for frontend"""
        try:
            # Subquery logic for consistent joins
            latest_ltp_subquery = db.query(
                StrikePriceTickData.symbol,
                func.max(StrikePriceTickData.id).label('max_id')
            ).group_by(StrikePriceTickData.symbol).subquery()

            ltp_join = db.query(
                StrikePriceTickData.symbol,
                StrikePriceTickData.ltp
            ).join(
                latest_ltp_subquery,
                StrikePriceTickData.id == latest_ltp_subquery.c.max_id
            ).subquery()

            result = db.query(Order, ltp_join.c.ltp.label('current_ltp')).outerjoin(
                ltp_join, Order.symbol == ltp_join.c.symbol
            ).options(
                joinedload(Order.strategy),
                joinedload(Order.signal_log)
            ).filter(
                Order.id == position_id
            ).first()
            
            if result:
                logger.info(f"Retrieved trade: {position_id}")
                return PositionService._transform_order_to_position(result.Order, result.current_ltp)
            return None
        except Exception as e:
            logger.error(f"Error retrieving trade {position_id}: {str(e)}")
            raise
