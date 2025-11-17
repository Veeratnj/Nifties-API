"""
Trade service - Business logic for trade operations
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.models import Trade
from app.schemas.schema import TradeCreate, TradeUpdate

logger = logging.getLogger(__name__)


class TradeService:
    """Service for trade operations"""

    @staticmethod
    def get_all_trades(db: Session, user_id: Optional[int] = None) -> List[Trade]:
        """Get all trades, optionally filtered by user"""
        try:
            query = db.query(Trade)
            if user_id:
                query = query.filter(Trade.user_id == user_id)
            trades = query.all()
            logger.info(f"Retrieved {len(trades)} trades")
            return trades
        except Exception as e:
            logger.error(f"Error retrieving trades: {str(e)}")
            raise

    @staticmethod
    def get_trade_by_id(db: Session, trade_id: int) -> Optional[Trade]:
        """Get trade by ID"""
        try:
            trade = db.query(Trade).filter(Trade.id == trade_id).first()
            if trade:
                logger.info(f"Retrieved trade: {trade_id}")
            return trade
        except Exception as e:
            logger.error(f"Error retrieving trade {trade_id}: {str(e)}")
            raise

    @staticmethod
    def create_trade(db: Session, trade_data: TradeCreate, user_id: int) -> Trade:
        """Create new trade"""
        try:
            # Calculate PnL
            pnl = (trade_data.current_price - trade_data.entry_price) * trade_data.qty
            pnl_percent = ((trade_data.current_price - trade_data.entry_price) / trade_data.entry_price) * 100
            
            new_trade = Trade(
                **trade_data.dict(),
                user_id=user_id,
                pnl=pnl,
                pnl_percent=pnl_percent
            )
            db.add(new_trade)
            db.commit()
            db.refresh(new_trade)
            logger.info(f"Created trade: {new_trade.id} for user: {user_id}")
            return new_trade
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating trade: {str(e)}")
            raise

    @staticmethod
    def update_trade(db: Session, trade_id: int, trade_data: TradeUpdate) -> Optional[Trade]:
        """Update trade"""
        try:
            trade = db.query(Trade).filter(Trade.id == trade_id).first()
            if not trade:
                logger.warning(f"Trade not found: {trade_id}")
                return None
            
            # Recalculate PnL if price changed
            if trade_data.current_price:
                pnl = (trade_data.current_price - trade.entry_price) * trade.qty
                pnl_percent = ((trade_data.current_price - trade.entry_price) / trade.entry_price) * 100
                trade.pnl = pnl
                trade.pnl_percent = pnl_percent
            
            update_data = trade_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                if key not in ['pnl', 'pnl_percent']:
                    setattr(trade, key, value)
            
            db.commit()
            db.refresh(trade)
            logger.info(f"Updated trade: {trade_id}")
            return trade
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating trade {trade_id}: {str(e)}")
            raise

    @staticmethod
    def delete_trade(db: Session, trade_id: int) -> bool:
        """Delete trade"""
        try:
            trade = db.query(Trade).filter(Trade.id == trade_id).first()
            if not trade:
                logger.warning(f"Trade not found: {trade_id}")
                return False
            
            db.delete(trade)
            db.commit()
            logger.info(f"Deleted trade: {trade_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting trade {trade_id}: {str(e)}")
            raise

    @staticmethod
    def get_active_trades(db: Session, user_id: int) -> List[Trade]:
        """Get active trades for user"""
        try:
            trades = db.query(Trade).filter(
                Trade.user_id == user_id,
                Trade.status == "ACTIVE"
            ).all()
            logger.info(f"Retrieved {len(trades)} active trades for user: {user_id}")
            return trades
        except Exception as e:
            logger.error(f"Error retrieving active trades: {str(e)}")
            raise

    @staticmethod
    def close_trade(db: Session, trade_id: int, closing_price: float) -> Optional[Trade]:
        """Close trade with final price"""
        try:
            trade = db.query(Trade).filter(Trade.id == trade_id).first()
            if not trade:
                return None
            
            trade.current_price = closing_price
            trade.status = "CLOSED"
            pnl = (closing_price - trade.entry_price) * trade.qty
            pnl_percent = ((closing_price - trade.entry_price) / trade.entry_price) * 100
            trade.pnl = pnl
            trade.pnl_percent = pnl_percent
            
            db.commit()
            db.refresh(trade)
            logger.info(f"Closed trade: {trade_id} with PnL: {pnl}")
            return trade
        except Exception as e:
            db.rollback()
            logger.error(f"Error closing trade {trade_id}: {str(e)}")
            raise
