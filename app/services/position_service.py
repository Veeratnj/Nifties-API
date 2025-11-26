"""
Position service - Business logic for position/live trades operations
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models.models import Position, Strategy
from app.schemas.schema import PositionCreate, PositionUpdate

logger = logging.getLogger(__name__)


class PositionService:
    """Service for position operations"""

    @staticmethod
    def get_all_positions(db: Session, user_id: Optional[int] = None, user_role: str = "USER") -> List[dict]:
        """
        Get positions based on user role:
        - SUPERADMIN/ADMIN: Get ALL positions from all users
        - USER/TRADER: Get only their own positions
        """
        try:
            query = db.query(Position).options(joinedload(Position.strategy))
            
            # Role-based filtering
            if user_role in ["SUPERADMIN", "ADMIN"]:
                # Admins see all positions
                logger.info(f"Admin user accessing all positions")
            else:
                # Regular users see only their positions
                if user_id:
                    query = query.filter(Position.user_id == user_id)
                    logger.info(f"User {user_id} accessing their positions")
            
            positions = query.all()
            logger.info(f"Retrieved {len(positions)} positions")
            
            # Transform to frontend format
            return [PositionService._transform_position(p) for p in positions]
        except Exception as e:
            logger.error(f"Error retrieving positions: {str(e)}")
            raise

    @staticmethod
    def _transform_position(position: Position) -> dict:
        """Transform Position model to frontend expected format"""
        # Calculate P&L if not set
        pnl = float(position.total_pnl or position.unrealized_pnl or 0)
        pnl_percent = float(position.pnl_percent or 0)
        
        # Get strategy name
        strategy_name = None
        if position.strategy:
            strategy_name = position.strategy.name
        
        # Map status
        status = "ACTIVE" if position.status.value == "OPEN" else "CLOSED"
        
        return {
            "id": position.id,
            "user_id": position.user_id,
            "symbol": position.symbol,
            "index": position.underlying,  # Map 'underlying' to 'index'
            "strike": position.strike_price,  # Map 'strike_price' to 'strike'
            "type": position.option_type,  # Map 'option_type' to 'type'
            "qty": position.qty,
            "entry_price": float(position.avg_entry_price),
            "current_price": float(position.avg_exit_price or position.avg_entry_price),
            "pnl": pnl,
            "pnl_percent": pnl_percent,
            "status": status,
            "strategy": strategy_name,
            "timestamp": position.entry_time,
            "created_at": position.entry_time,
            "updated_at": position.updated_at or position.entry_time
        }

    @staticmethod
    def get_active_positions(db: Session, user_id: int) -> List[dict]:
        """Get active/open positions for user, formatted for frontend"""
        try:
            positions = db.query(Position).options(joinedload(Position.strategy)).filter(
                Position.user_id == user_id,
                Position.status == "OPEN"
            ).all()
            
            logger.info(f"Retrieved {len(positions)} active positions for user: {user_id}")
            return [PositionService._transform_position(p) for p in positions]
        except Exception as e:
            logger.error(f"Error retrieving active positions: {str(e)}")
            raise

    @staticmethod
    def get_position_by_id(db: Session, position_id: int) -> Optional[dict]:
        """Get position by ID, formatted for frontend"""
        try:
            position = db.query(Position).options(joinedload(Position.strategy)).filter(
                Position.id == position_id
            ).first()
            
            if position:
                logger.info(f"Retrieved position: {position_id}")
                return PositionService._transform_position(position)
            return None
        except Exception as e:
            logger.error(f"Error retrieving position {position_id}: {str(e)}")
            raise
