"""
Market service - Business logic for market data
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.models import MarketIndex, PnLSnapshot, SymbolMaster
from app.schemas.schema import MarketIndexSchema, MarketIndexCreate, MarketIndexUpdate, PnLSchema, PnLCreate

logger = logging.getLogger(__name__)


class MarketService:
    """Service for market data operations"""

    @staticmethod
    def get_all_indices(db: Session) -> List[MarketIndex]:
        """Get all market indices"""
        try:
            indices = db.query(SymbolMaster).filter(
                SymbolMaster.is_active == True and 
                SymbolMaster.is_deleted == False and
                SymbolMaster.instrument_type == 'INDEX').all()
            logger.info(f"Retrieved {len(indices)} market indices")
            return indices
        except Exception as e:
            logger.error(f"Error retrieving market indices: {str(e)}")
            raise

    @staticmethod
    def get_index_by_name(db: Session, name: str) -> Optional[MarketIndex]:
        """Get market index by name"""
        try:
            index = db.query(MarketIndex).filter(MarketIndex.name == name).first()
            if index:
                logger.info(f"Retrieved market index: {name}")
            return index
        except Exception as e:
            logger.error(f"Error retrieving market index {name}: {str(e)}")
            raise

    @staticmethod
    def create_index(db: Session, index_data: MarketIndexCreate) -> MarketIndex:
        """Create new market index"""
        try:
            new_index = MarketIndex(**index_data.dict())
            db.add(new_index)
            db.commit()
            db.refresh(new_index)
            logger.info(f"Created market index: {new_index.name}")
            return new_index
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating market index: {str(e)}")
            raise

    @staticmethod
    def update_index(db: Session, index_id: int, index_data: MarketIndexUpdate) -> Optional[MarketIndex]:
        """Update market index"""
        try:
            index = db.query(MarketIndex).filter(MarketIndex.id == index_id).first()
            if not index:
                logger.warning(f"Market index not found: {index_id}")
                return None
            
            update_data = index_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(index, key, value)
            
            db.commit()
            db.refresh(index)
            logger.info(f"Updated market index: {index_id}")
            return index
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating market index {index_id}: {str(e)}")
            raise

    @staticmethod
    def delete_index(db: Session, index_id: int) -> bool:
        """Delete market index"""
        try:
            index = db.query(MarketIndex).filter(MarketIndex.id == index_id).first()
            if not index:
                logger.warning(f"Market index not found: {index_id}")
                return False
            
            db.delete(index)
            db.commit()
            logger.info(f"Deleted market index: {index_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting market index {index_id}: {str(e)}")
            raise


    @staticmethod
    def get_all_pnl(db: Session) -> List[PnLSnapshot]:
        """Get all PnL records"""
        try:
            pnl_records = db.query(PnLSnapshot).all()
            logger.info(f"Retrieved {len(pnl_records)} PnL records")
            return pnl_records
        except Exception as e:
            logger.error(f"Error retrieving PnL records: {str(e)}")
            raise


    @staticmethod
    def get_pnl_by_period(db: Session, period: str) -> Optional[PnLSnapshot]:
        """Get PnL by period"""
        try:
            pnl = db.query(PnLSnapshot).filter(PnLSnapshot.snapshot_type == period).first()
            if pnl:
                logger.info(f"Retrieved PnL for period: {period}")
            return pnl
        except Exception as e:
            logger.error(f"Error retrieving PnL for period {period}: {str(e)}")
            raise

    @staticmethod
    def create_pnl(db: Session, pnl_data: PnLCreate) -> PnLSnapshot:
        """Create new PnL record"""
        try:
            new_pnl = PnLSnapshot(**pnl_data.dict())
            db.add(new_pnl)
            db.commit()
            db.refresh(new_pnl)
            logger.info(f"Created PnL record for period: {new_pnl.snapshot_type}")
            return new_pnl
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating PnL record: {str(e)}")
            raise
