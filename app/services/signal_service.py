"""
Service layer for Signal operations
"""
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo

from app.schemas.signal_schema import SignalEntryRequest, SignalExitRequest
from app.models.models import SignalLog


class SignalService:
    """Service class for trading signal operations"""
    
    @staticmethod
    def process_entry_signal(db: Session, signal_data: SignalEntryRequest) -> Dict[str, Any]:
        """
        Process entry signal and store in database
        
        Args:
            db: Database session
            signal_data: Entry signal data
            
        Returns:
            Dictionary with processed signal information
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # Create signal log entry
            signal_log = SignalLog(
                token=signal_data.token,
                signal_type=signal_data.signal,
                unique_id=signal_data.unique_id,
                strike_price_token=signal_data.strike_price_token,
                strategy_code=signal_data.strategy_code,
                signal_category="ENTRY",
                timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
            )
            
            db.add(signal_log)
            db.commit()
            db.refresh(signal_log)
            
            return {
                "id": signal_log.id,
                "token": signal_log.token,
                "signal": signal_log.signal_type,
                "unique_id": signal_log.unique_id,
                "strike_price_token": signal_log.strike_price_token,
                "strategy_code": signal_log.strategy_code,
                "timestamp": signal_log.timestamp.isoformat()
            }
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to process entry signal: {str(e)}")
    
    @staticmethod
    def process_exit_signal(db: Session, signal_data: SignalExitRequest) -> Dict[str, Any]:
        """
        Process exit signal and store in database
        
        Args:
            db: Database session
            signal_data: Exit signal data
            
        Returns:
            Dictionary with processed signal information
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # Create signal log entry
            signal_log = SignalLog(
                token=signal_data.token,
                signal_type=signal_data.signal,
                unique_id=signal_data.unique_id,
                strike_price_token=signal_data.strike_price_token,
                strategy_code=signal_data.strategy_code,
                signal_category="EXIT",
                timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
            )
            
            db.add(signal_log)
            db.commit()
            db.refresh(signal_log)
            
            return {
                "id": signal_log.id,
                "token": signal_log.token,
                "signal": signal_log.signal_type,
                "unique_id": signal_log.unique_id,
                "strike_price_token": signal_log.strike_price_token,
                "strategy_code": signal_log.strategy_code,
                "timestamp": signal_log.timestamp.isoformat()
            }
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to process exit signal: {str(e)}")
