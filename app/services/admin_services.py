


from app.schemas.signal_schema import SignalEntryRequest, SignalExitRequest
from app.models.models import SignalLog, StrikeInstrument, Strategy
from app.utils.security import get_all_traders_id
from app.utils.broker_dhan_api import call_broker_dhan_api
import threading
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from app.services.order_service_utils import get_all_traders_id,call_broker_dhan_api


class AdminService:
    

    @staticmethod
    def create_live_trade_for_all_users_v1(signal_data:SignalEntryRequest,db:Session):
        
        strategy_id = (
            db.query(Strategy.id)
            .filter(Strategy.name == signal_data.strategy_code)
            .first()
        )
        

        db.add(SignalLog(
            token=signal_data.token,
            signal_type=signal_data.signal,
            unique_id=signal_data.unique_id,
            strike_price_token=signal_data.strike_data.token,
            strategy_code=signal_data.strategy_code,
            signal_category="ENTRY",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
        ))
        db.commit()
        
        signal_log = db.query(SignalLog).filter(SignalLog.unique_id == signal_data.unique_id).order_by(SignalLog.id.desc()).first()
        signal_log_id = signal_log.id if signal_log else None
        traders_ids = get_all_traders_id(db=db)
        db.add(StrikeInstrument(
            token=signal_data.strike_data.token,
            symbol=signal_data.strike_data.symbol,
            exchange=signal_data.strike_data.exchange,
            is_started=False,
            is_deleted=False
        ))
        db.commit()

        for trader_id in traders_ids:
            threading.Thread(target=call_broker_dhan_api, args=(trader_id,signal_log_id,signal_data,)).start()
        return True


    @staticmethod
    def create_live_trade_for_user_v1(signal_data:SignalEntryRequest,user_ids:List[int],db:Session):

        strategy_id = (
            db.query(Strategy.id)
            .filter(Strategy.name == signal_data.strategy_code)
            .first()
        )
        

        db.add(SignalLog(
            token=signal_data.token,
            signal_type=signal_data.signal,
            unique_id=signal_data.unique_id,
            strike_price_token=signal_data.strike_data.token,
            strategy_code=signal_data.strategy_code,
            signal_category="ENTRY",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
        ))
        db.commit()
        
        signal_log = db.query(SignalLog).filter(SignalLog.unique_id == signal_data.unique_id).order_by(SignalLog.id.desc()).first()
        signal_log_id = signal_log.id if signal_log else None
        db.add(StrikeInstrument(
            token=signal_data.strike_data.token,
            symbol=signal_data.strike_data.symbol,
            exchange=signal_data.strike_data.exchange,
            is_started=False,
            is_deleted=False
        ))
        db.commit()

        for trader_id in user_ids:
            threading.Thread(target=call_broker_dhan_api, args=(trader_id,signal_log_id,signal_data,)).start()


    @staticmethod
    def close_live_trade_for_all_users_v1(db):
        signal_log_id = db.query(SignalLog.id).filter(SignalLog.unique_id == signal_data.unique_id).scalar()
        db.add(SignalLog(
            token=signal_data.token,
            signal_type=signal_data.signal,
            unique_id=signal_data.unique_id,
            strike_price_token=signal_data.strike_data.token,
            strategy_code=signal_data.strategy_code,
            signal_category="EXIT",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
        ))
        db.commit()

        traders_ids = get_all_traders_id(db=db)

        for trader_id in traders_ids:
            threading.Thread(target=call_broker_dhan_api, args=(trader_id,signal_log_id,signal_data)).start()

    @staticmethod
    def close_live_trade_for_user_v1(signal_data:SignalExitRequest,user_ids:List[int],db:Session):
        signal_log_id = db.query(SignalLog.id).filter(SignalLog.unique_id == signal_data.unique_id).scalar()
        db.add(SignalLog(
            token=signal_data.token,
            signal_type=signal_data.signal,
            unique_id=signal_data.unique_id,
            strike_price_token=signal_data.strike_data.token,
            strategy_code=signal_data.strategy_code,
            signal_category="EXIT",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
        ))
        db.commit()


        for trader_id in user_ids:
            threading.Thread(target=call_broker_dhan_api, args=(trader_id,signal_log_id,signal_data)).start()


























