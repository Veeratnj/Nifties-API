


from app.schemas.signal_schema import SignalEntryRequest, SignalExitRequest ,StrikeData
from app.models.models import SignalLog, StrikeInstrument, Strategy , Order , StrikePriceTickData
import threading
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.services.order_service_utils import get_all_traders_id
from datetime import date, timedelta
from app.services.signal_service import SignalService
from typing import List

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

    @staticmethod
    def update_stop_loss_target_v1(unique_id:str,stop_loss:float,target:float,db:Session):
        signal_log = db.query(SignalLog).filter(SignalLog.signal_category == "ENTRY",SignalLog.unique_id == unique_id).order_by(SignalLog.id.desc()).first()
        signal_log.stop_loss = stop_loss
        signal_log.target = target
        # signal_log.payload["stop_loss"] = stop_loss
        # signal_log.payload["target"] = target
        db.commit()
        return True




    @staticmethod
    def show_all_today_live_trades_v10(db: Session):
        today = date.today()
        tomorrow = today + timedelta(days=1)

        subq = (
            db.query(
                SignalLog.unique_id,
                func.count(SignalLog.unique_id).label("signal_count")
            )
            .filter(
                SignalLog.timestamp >= today,
                SignalLog.timestamp < tomorrow
            )
            .group_by(SignalLog.unique_id)
            .subquery()
        )

        rows = (
            db.query(
                SignalLog.payload,
                SignalLog.stop_loss,
                SignalLog.target,
                subq.c.signal_count
            )
            .join(subq, SignalLog.unique_id == subq.c.unique_id)
            .filter(
                SignalLog.timestamp >= today,
                SignalLog.timestamp < tomorrow,
                SignalLog.signal_category == "ENTRY"
            )
            .order_by(SignalLog.id.desc())
            .all()
        )

        return [
            {
                **(payload or {}),
                "stop_loss": stop_loss,
                "target": target,
                "signal_count": signal_count,
                "status": "OPEN" if signal_count == 1 else "CLOSED",
                'current_price':30,
                'entry_price':20
            }
            for payload, stop_loss, target, signal_count in rows
        ]



    @staticmethod
    def show_all_today_live_trades_v1(db: Session, user_id: int = 2):
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # -----------------------------
        # Subquery: count signals per unique_id
        # -----------------------------
        subq = (
            db.query(
                SignalLog.unique_id,
                func.count(SignalLog.unique_id).label("signal_count")
            )
            .filter(
                SignalLog.timestamp >= today,
                SignalLog.timestamp < tomorrow
            )
            .group_by(SignalLog.unique_id)
            .subquery()
        )

        # -----------------------------
        # Main query (ENTRY signals only)
        # -----------------------------
        rows = (
            db.query(
                SignalLog.id,
                SignalLog.token,
                SignalLog.payload,
                SignalLog.stop_loss,
                SignalLog.target,
                subq.c.signal_count
            )
            .join(subq, SignalLog.unique_id == subq.c.unique_id)
            .filter(
                SignalLog.timestamp >= today,
                SignalLog.timestamp < tomorrow,
                SignalLog.signal_category == "ENTRY"
            )
            .order_by(SignalLog.id.desc())
            .all()
        )

        results = []

        for signal_id, token, payload, stop_loss, target, signal_count in rows:
            data = dict(payload) if payload else {}

            # -----------------------------
            # Entry price
            # -----------------------------
            entry_price = (
                db.query(Order.entry_price)
                .filter(
                    Order.user_id == user_id,
                    Order.signal_log_id == signal_id,
                    Order.is_deleted == False
                )
                .scalar()
            )

            # -----------------------------
            # Exit price (if exited)
            # -----------------------------
            exit_price = (
                db.query(Order.exit_price)
                .filter(
                    Order.user_id == user_id,
                    Order.signal_log_id == signal_id,
                    Order.is_deleted == False
                )
                .scalar()
            )
            print(exit_price)
            print(payload['strike_data'])

            # -----------------------------
            # Current price
            # -----------------------------
            if exit_price is not None and exit_price != 0:
                current_price = exit_price
                print('123')
            else:
                current_price = (
                    db.query(StrikePriceTickData.ltp)
                    .filter(
                        StrikePriceTickData.token == payload["strike_data"]["token"],
                    )
                    .order_by(StrikePriceTickData.id.desc())  # latest row first
                    .limit(1)                               # only 1 row
                    .scalar()
                )

                print(payload["strike_data"]["token"])

            # -----------------------------
            # Final response object
            # -----------------------------
            data.update({
                "stop_loss": stop_loss,
                "target": target,
                "signal_count": signal_count,
                "status": "OPEN" if signal_count == 1 else "CLOSED",
                "entry_price": entry_price,
                "current_price": current_price
            })

            results.append(data)

        return results



    @staticmethod
    def kill_trade_v1(unique_id:str,db:Session):
        payload = db.query(SignalLog.payload).filter(SignalLog.unique_id == unique_id).order_by(SignalLog.id.desc()).first()
        # {
        #     "token": "27",
        #     "signal": "SELL_ENTRY",
        #     "target": 350.0,
        #     "stop_loss": 124.5,
        #     "unique_id": "a8f73199-446a-4cb4-84d0-c56e83d8a35a",
        #     "description": "qwerty",
        #     "strike_data": {
        #         "DOE": "2026-01-30",
        #         "token": "55116",
        #         "symbol": "NIFTY30JAN19500CE",
        #         "lot_qty": 50,
        #         "exchange": "NSE",
        #         "position": "CE",
        #         "index_name": "NIFTY",
        #         "strike_price": 19500
        #     },
        #     "strategy_code": "DAIKOKUTEN"
        # }
        print(payload)
        payload=payload[0]
        strike_data = StrikeData(
            token=payload["strike_data"]["token"],
            symbol=payload["strike_data"]["symbol"],
            exchange=payload["strike_data"]["exchange"],
            position=payload["strike_data"]["position"],
            index_name=payload["strike_data"]["index_name"],
            strike_price=payload["strike_data"]["strike_price"],
            DOE=payload["strike_data"]["DOE"],
            lot_qty=payload["strike_data"]["lot_qty"],
        )
        Payload = SignalExitRequest(
            token=payload["token"],
            signal= 'BUY_EXIT' if payload["signal"] == 'BUY_ENTRY' else 'SELL_EXIT',
            unique_id=payload["unique_id"],
            strike_data=strike_data,
            strategy_code=payload["strategy_code"],
            signal_category="EXIT",
            stop_loss=payload["stop_loss"],
            target=payload["target"],
            description=payload["description"],
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
        )
        print(123)
        SignalService.process_exit_signal_v3(signal_data=Payload,db=db)
        return True





















