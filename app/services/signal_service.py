"""
Service layer for Signal operations
"""
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from dhanhq import dhanhq, DhanContext



from app.schemas.signal_schema import SignalEntryRequest, SignalExitRequest
from app.models.models import SignalLog, Order, Position , Trade , Strategy
from app.services.order_service_utils import get_all_traders_id,get_dhan_credentials,call_broker_dhan_api
from app.services.broker_services import place_dhan_order_standalone


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










    @staticmethod
    def process_entry_signal_v3(db: Session, signal_data: SignalEntryRequest) -> Dict[str, Any]:

        print('check point 0')
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
            strike_price_token=signal_data.strike_price_token,
            strategy_code=signal_data.strategy_code,
            signal_category="ENTRY",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
        ))
        db.commit()
        print('check point 1')
        
        signal_log = db.query(SignalLog).filter(SignalLog.unique_id == signal_data.unique_id).order_by(SignalLog.id.desc()).first()
        signal_log_id = signal_log.id if signal_log else None
        traders_ids = get_all_traders_id(db=db)
        print('check point 2')

        for trader_id in traders_ids:
            threading.Thread(target=call_broker_dhan_api, args=(trader_id,signal_log_id,signal_data,db)).start()
        print('check point 3')
            # dhan_creds=get_dhan_credentials(trader_id=trader_id)
            # if dhan_creds:
            #     DhanContext(client_id=dhan_creds['client_id'], access_token=dhan_creds['access_token'])
            #     dhan = dhanhq(dhan_context)
            #     dhan_res = dhan.place_order(
            #     security_id=signal_data.token,
            #     exchange_segment=dhan.NSE_FNO,
            #     transaction_type=dhan.BUY if signal_data.signal.lower() == 'buy_entry' else dhan.SELL,
            #     quantity=35,
            #     order_type=dhan.MARKET,
            #     product_type=dhan.INTRA,
            #     price=0,
            #     )
            #     db.add(
            #         Order(
            #             user_id=trader_id,
            #             signal_log_id=signal_log_id,
            #             symbol=signal_data.strike_price_token,
            #             option_type="CE",
            #             qty=35,
            #             entry_price=0,
            #             status="OPEN",
            #             entry_time=datetime.now(ZoneInfo("Asia/Kolkata")),
            #             is_deleted=False
            #         )
            #     )
                

    @staticmethod
    def process_exit_signal_v3(db: Session, signal_data: SignalExitRequest) -> Dict[str, Any]:
        db.add(SignalLog(
            token=signal_data.token,
            signal_type=signal_data.signal,
            unique_id=signal_data.unique_id,
            strike_price_token=signal_data.strike_price_token,
            strategy_code=signal_data.strategy_code,
            signal_category="EXIT",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
        ))
        db.commit()

        signal_log_id = db.query(SignalLog.id).filter(SignalLog.unique_id == signal_data.unique_id).scalar()
        traders_ids = get_all_traders_id(db=db)

        for trader_id in traders_ids:
            threading.Thread(target=call_broker_dhan_api, args=(trader_id,signal_log_id,signal_data)).start()


            



        





