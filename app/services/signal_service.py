"""
Service layer for Signal operations
"""
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from dhanhq import dhanhq, DhanContext
from fastapi import Request



from app.schemas.signal_schema import SignalEntryRequest, SignalExitRequest
from app.models.models import SignalLog, Order, Position , Trade , Strategy ,StrikeInstrument
from app.services.order_service_utils import get_all_traders_id,get_dhan_credentials,call_broker_api
from app.services.broker_services import place_dhan_order_standalone
from app.services.order_service_utils import get_angelone_symbol


import threading

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
                strike_price_token=signal_data.strike_data.token,
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
                strike_price_token=signal_data.strike_data.token,
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










    @staticmethod
    def process_entry_signal_v3(db: Session, signal_data: SignalEntryRequest,request:Request) -> Dict[str, Any]:

        print('check point 0',signal_data.strike_data.token)
        strategy_id = (
            db.query(Strategy.id)
            .filter(Strategy.name == signal_data.strategy_code)
            .first()
        )
        
        print('strategy id',strategy_id)

        db.add(SignalLog(
            token=signal_data.token,
            signal_type=signal_data.signal,
            unique_id=signal_data.unique_id,
            strike_price_token=signal_data.strike_data.token,
            strategy_code=signal_data.strategy_code,
            signal_category="ENTRY",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata")),
            payload=signal_data.model_dump(mode="json"),
            stop_loss=signal_data.stop_loss,
            target=signal_data.target,
            description=signal_data.description
        ))
        db.commit()
        print('check point 1')
        
        signal_log = db.query(SignalLog).filter(SignalLog.unique_id == signal_data.unique_id).order_by(SignalLog.id.desc()).first()
        signal_log_id = signal_log.id if signal_log else None
        traders_ids = get_all_traders_id(db=db)
        print('check point 2')
        db.add(StrikeInstrument(
            token=signal_data.strike_data.token,
            symbol=signal_data.strike_data.symbol,
            exchange=signal_data.strike_data.exchange,
            is_started=False,
            is_deleted=False
        ))
        db.commit()
        # import pandas as pd
        # df=pd.read_csv('OpenAPIScripMaster.csv')

        # angelone_symbol = (
        #     df.loc[df['token'] == int(signal_data.strike_data.token), 'symbol']
        #     .iloc[0]
        #     if not df[df['token'] == int(signal_data.strike_data.token)].empty
        #     else None
        # )
        angelone_symbol=get_angelone_symbol(token=int(signal_data.strike_data.token))


        for trader_id in traders_ids:
            threading.Thread(target=call_broker_api, args=(trader_id,signal_log_id,angelone_symbol,signal_data,)).start()
        print('check point 3')
            
                

    @staticmethod
    def process_exit_signal_v3(db: Session, signal_data: SignalExitRequest) -> Dict[str, Any]:
        signal_log_id = db.query(SignalLog.id).filter(SignalLog.unique_id == signal_data.unique_id).scalar()
        print('exit check point 0',signal_log_id)
        db.add(SignalLog(
            token=signal_data.token,
            signal_type=signal_data.signal,
            unique_id=signal_data.unique_id,
            strike_price_token=signal_data.strike_data.token,
            strategy_code=signal_data.strategy_code,
            signal_category="EXIT",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata")),
            payload=signal_data.model_dump(mode="json"),
            stop_loss=0.0,
            target=0.0,
            description=signal_data.description
        ))
        db.commit()
        print('exit check point 1')

        print('exit check point 2',signal_log_id)
        traders_ids = get_all_traders_id(db=db)
        print('exit check point 3',traders_ids)
        angelone_symbol=get_angelone_symbol(token=int(signal_data.strike_data.token))

        for trader_id in traders_ids:
            threading.Thread(target=call_broker_dhan_api, args=(trader_id,signal_log_id,angelone_symbol,signal_data)).start()


            



        





