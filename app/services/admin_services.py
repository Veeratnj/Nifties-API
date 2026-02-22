


from app.schemas.signal_schema import SignalEntryRequest, SignalExitRequest ,StrikeData
from app.models.models import SignalLog, StrikeInstrument, Strategy , Order , StrikePriceTickData ,SymbolMaster,User,DhanCredentials,AngelOneCredentials , ScriptsInfo , AdminDhanCreds
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
    def update_stop_loss_target_v1(unique_id:str,stop_loss:float,target:float,strike_price_stop_loss:float,strike_price_target:float,db:Session):
        signal_log = db.query(SignalLog).filter(SignalLog.signal_category == "ENTRY",SignalLog.unique_id == unique_id).order_by(SignalLog.id.desc()).first()
        signal_log.stop_loss = stop_loss
        signal_log.target = target
        signal_log.strike_price_stop_loss = strike_price_stop_loss
        signal_log.strike_price_target = strike_price_target
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
                SignalLog.strike_price_stop_loss,
                SignalLog.strike_price_target,
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

        for signal_id, token, payload, stop_loss, target, strike_price_stop_loss, strike_price_target, signal_count in rows:
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
                ).limit(1)
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
                ).limit(1)
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
                "current_price": current_price,
                "strike_price_stop_loss": strike_price_stop_loss,
                "strike_price_target": strike_price_target,
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

    @staticmethod
    def get_all_instruments_v1(db:Session):
        result = db.query(
            SymbolMaster.token.label("token"),
            SymbolMaster.symbol.label("symbol"),
            SymbolMaster.exchange.label("exchange"),
            SymbolMaster.instrument_type.label("instrument_type"),
            SymbolMaster.is_active.label("is_active"),
        ).all()

        return [
                {
                    "token": r.token,
                    "symbol": r.symbol,
                    "exchange": r.exchange,
                    "instrument_type": r.instrument_type,
                    "is_active": r.is_active,
                }
                for r in result
            ]

    @staticmethod
    def edit_instrument_v1(instrument_info, db: Session):
        rows_updated = (
                    db.query(SymbolMaster)
                    .filter(SymbolMaster.token == instrument_info.token)
                    .update(
                    {
                        SymbolMaster.symbol: instrument_info.symbol,
                        SymbolMaster.exchange: instrument_info.exchange,
                        SymbolMaster.instrument_type: instrument_info.instrument_type,
                        SymbolMaster.is_active: instrument_info.is_active,
                        SymbolMaster.is_deleted: not instrument_info.is_active,
                        SymbolMaster.updated_at: datetime.now(ZoneInfo("Asia/Kolkata")),
                    },
                    synchronize_session=False,
                )
            )

        if rows_updated == 0:
            db.rollback()
            return False  # token not found

        db.commit()
        return True


    @staticmethod
    def get_all_users_info_v(db:Session):
        # users= db.query(
        #     User.id.label("user_id"),
        #     User.name.label("name"),
        #     User.email.label("email"),
        #     User.phone.label("phone"),
        #     User.role.label("role"),
        #     User.is_active.label("is_active"),
        # ).all()

        # dhan_accounts = db.query(
        #     DhanAccount.user_id.label("user_id"),
        #     DhanAccount.client_id.label("client_id"),
        #     DhanAccount.access_token.label("access_token"),
        #     DhanAccount.is_active.label("is_active"),
        # ).all()

        # angel_accounts = db.query(
        #     AngelOneCredentials.user_id.label("user_id"),
        #     AngelOneCredentials.api_key.label("api_key"),
        #     AngelOneCredentials.username.label("username"),
        #     AngelOneCredentials.password.label("password"),
        #     AngelOneCredentials.token.label("token"),
        #     AngelOneCredentials.is_active.label("is_active"),
        # ).all()
        print(123)
        users = (
                db.query(User)
                .options(
                    joinedload(User.dhan_info),
                    joinedload(User.angelone_info),
                )
                .all()
            )
        print(users)
        return users


    @staticmethod
    def get_all_users_info_v1(db: Session):
        rows = (
            db.query(
                User.id.label("user_id"),
                User.username,
                User.email,
                User.phone,
                User.role,
                User.is_active,
                DhanCredentials.client_id,
                DhanCredentials.access_token,
                DhanCredentials.is_active.label("dhan_is_active"),
                AngelOneCredentials.username.label("angelone_username"),
                AngelOneCredentials.password.label("angelone_password"),
                AngelOneCredentials.token.label("angelone_token"),
                AngelOneCredentials.api_key.label("angelone_api_key"),
                AngelOneCredentials.is_active.label("angelone_is_active"),
            )
            .outerjoin(DhanCredentials, DhanCredentials.user_id == User.id)
            .outerjoin(AngelOneCredentials, AngelOneCredentials.user_id == User.id)
            .order_by(User.id)
            .all()
        )

        # ---- Transform flat rows → nested Pydantic structure ----
        users = []
        for r in rows:
            user_dict = {
                "user_id": r.user_id,
                "name": r.username,
                "email": r.email,
                "phone": r.phone,
                "role": r.role,
                "is_active": r.is_active,
                "dhan_info": None,
                "angelone_info": None,
            }

            if r.client_id:   # means Dhan exists
                user_dict["dhan_info"] = {
                    "client_id": r.client_id,
                    "access_token": r.access_token,
                    "is_active": r.dhan_is_active,
                }

            if r.angelone_username:  # means AngelOne exists
                user_dict["angelone_info"] = {
                    "api_key": r.angelone_api_key,
                    "username": r.angelone_username,
                    "password": r.angelone_password,
                    "token": r.angelone_token,
                    "is_active": r.angelone_is_active,
                }

            users.append(user_dict)

        return users


    @staticmethod
    def update_user_broker_details_v1(broker_details,db:Session):
        user_id = broker_details.user_id
        dhan_info = broker_details.dhan_info
        angelone_info = broker_details.angelone_info
      
        if dhan_info:
            db.query(DhanCredentials).filter(DhanCredentials.user_id == user_id).update({
                DhanCredentials.client_id: dhan_info.client_id,
                DhanCredentials.access_token: dhan_info.access_token,
                DhanCredentials.is_active: dhan_info.is_active,
            })
        if angelone_info:
            db.query(AngelOneCredentials).filter(AngelOneCredentials.user_id == user_id).update({
                AngelOneCredentials.api_key: angelone_info.api_key,
                AngelOneCredentials.username: angelone_info.username,
                AngelOneCredentials.password: angelone_info.password,
                AngelOneCredentials.token: angelone_info.token,
                AngelOneCredentials.is_active: angelone_info.is_active,
            })
        db.commit()

        return True


    @staticmethod
    def get_status_of_scripts_v1(db:Session):
        pass


    @staticmethod
    def list_scripts_v1(db:Session):
        scripts = db.query(ScriptsInfo.id,
        ScriptsInfo.name,
        ScriptsInfo.is_started).all()

        scripts_list = []
        for script in scripts:
            scripts_list.append({
                "id": script.id,
                "name": script.name,
                "is_started": script.is_started,
            })
        return scripts_list    
        


    @staticmethod
    def update_strike_price_stop_loss_target_v1(
        unique_id: str,
        strike_price_stop_loss: float,
        strike_price_target: float,
        db: Session
    ):
        signal_log = (
            db.query(SignalLog)
            .filter(
                SignalLog.signal_category == "ENTRY",
                SignalLog.unique_id == unique_id
            )
            .order_by(SignalLog.id.desc())
            .first()
        )

        if not signal_log:
            return False  # No matching entry found

        signal_log.strike_price_stop_loss = strike_price_stop_loss
        signal_log.strike_price_target = strike_price_target

        db.commit()
        db.refresh(signal_log)   # Optional but recommended

        return True

    @staticmethod
    def get_all_users_dhan_creds(db:Session):
        dhan_info = db.query(DhanCredentials).all()
        dhan_list = []
        for dhan in dhan_info:
            dhan_list.append({
                "user_name":dhan.user.username,
                "user_id":dhan.user.id,
                "client_id": dhan.client_id,
                "access_token": dhan.access_token,
                "is_active": dhan.is_active,
            })
        return dhan_list


    @staticmethod
    def get_admin_dhan_creds(db:Session):
        dhan_info = db.query(AdminDhanCreds).all()
        dhan_list = []
        for dhan in dhan_info:
            dhan_list.append({
                'id':dhan.id,
                "client_id": dhan.client_id,
                "access_token": dhan.access_token,
            })
        return dhan_list


    @staticmethod
    def update_admin_dhan_creds(db:Session,dhan_id:int,access_token:str,client_id:str):
        admin_dhan_creds = db.query(AdminDhanCreds).filter(AdminDhanCreds.id == dhan_id).first()
        if not admin_dhan_creds:
            return False
        admin_dhan_creds.access_token = access_token
        admin_dhan_creds.client_id = client_id
        db.commit()
        db.refresh(admin_dhan_creds)
        return True

    @staticmethod
    def update_user_dhan_creds(db:Session,user_id:int,access_token:str,client_id:str):
        user_dhan_creds = db.query(DhanCredentials).filter(DhanCredentials.user_id == user_id).first()
        if not user_dhan_creds:
            return False
        user_dhan_creds.access_token = access_token
        user_dhan_creds.client_id = client_id
        db.commit()
        db.refresh(user_dhan_creds)
        return True
        
        









