"""
Strategy service - Business logic for strategy operations
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.models import Strategy
from app.schemas.schema import StrategyCreate, StrategyUpdate

logger = logging.getLogger(__name__)


class StrategyService:
    """Service for strategy operations"""

    @staticmethod
    def get_all_strategies(db: Session, user_id: Optional[int] = None) -> List[Strategy]:
        """Get all strategies, optionally filtered by user"""
        try:
            query = db.query(Strategy)
            if user_id:
                query = query.filter(Strategy.user_id == user_id)
            strategies = query.all()
            logger.info(f"Retrieved {len(strategies)} strategies")
            return strategies
        except Exception as e:
            logger.error(f"Error retrieving strategies: {str(e)}")
            raise

    @staticmethod
    def get_strategy_by_id(db: Session, strategy_id: int) -> Optional[Strategy]:
        """Get strategy by ID"""
        try:
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if strategy:
                logger.info(f"Retrieved strategy: {strategy_id}")
            return strategy
        except Exception as e:
            logger.error(f"Error retrieving strategy {strategy_id}: {str(e)}")
            raise

    @staticmethod
    def create_strategy(db: Session, strategy_data: StrategyCreate, user_id: int) -> Strategy:
        """Create new strategy"""
        try:
            new_strategy = Strategy(
                **strategy_data.dict(),
                user_id=user_id
            )
            db.add(new_strategy)
            db.commit()
            db.refresh(new_strategy)
            logger.info(f"Created strategy: {new_strategy.id} - {new_strategy.name} for user: {user_id}")
            return new_strategy
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating strategy: {str(e)}")
            raise

    @staticmethod
    def update_strategy(db: Session, strategy_id: int, strategy_data: StrategyUpdate) -> Optional[Strategy]:
        """Update strategy"""
        try:
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                logger.warning(f"Strategy not found: {strategy_id}")
                return None
            
            update_data = strategy_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(strategy, key, value)
            
            db.commit()
            db.refresh(strategy)
            logger.info(f"Updated strategy: {strategy_id}")
            return strategy
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating strategy {strategy_id}: {str(e)}")
            raise

    @staticmethod
    def delete_strategy(db: Session, strategy_id: int) -> bool:
        """Delete strategy"""
        try:
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                logger.warning(f"Strategy not found: {strategy_id}")
                return False
            
            db.delete(strategy)
            db.commit()
            logger.info(f"Deleted strategy: {strategy_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting strategy {strategy_id}: {str(e)}")
            raise

    @staticmethod
    def get_active_strategies(db: Session, user_id: int) -> List[Strategy]:
        """Get active strategies for user"""
        try:
            strategies = db.query(Strategy).filter(
                Strategy.user_id == user_id,
                Strategy.status == "ACTIVE"
            ).all()
            logger.info(f"Retrieved {len(strategies)} active strategies for user: {user_id}")
            return strategies
        except Exception as e:
            logger.error(f"Error retrieving active strategies: {str(e)}")
            raise

    @staticmethod
    def update_strategy_pnl(db: Session, strategy_id: int, pnl: float, trade_count: int, win_count: int) -> Optional[Strategy]:
        """Update strategy PnL and statistics"""
        try:
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                return None
            
            strategy.current_pnl = pnl
            strategy.trades = trade_count
            if trade_count > 0:
                strategy.win_rate = (win_count / trade_count) * 100
            
            db.commit()
            db.refresh(strategy)
            logger.info(f"Updated strategy PnL: {strategy_id} - PnL: {pnl}")
            return strategy
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating strategy PnL {strategy_id}: {str(e)}")
            raise
