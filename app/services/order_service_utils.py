
from datetime import datetime
from zoneinfo import ZoneInfo
from app.models.models import Order, User, DhanCredentials , StrikePriceTickData , AngelOneCredentials
from sqlalchemy.orm import Session
from typing import List
from dhanhq import dhanhq, DhanContext
from fastapi import Request
import time
from SmartApi import SmartConnect
import pyotp


def get_all_traders_id(db: Session) -> List[int]:
    return list(map(lambda x: x.id, db.query(User.id).filter(User.role == "TRADER").all()))



def get_dhan_credentials(trader_id: int, db: Session) -> dict[str, str]:
    return db.query(
        DhanCredentials.client_id.label('client_id'),
        DhanCredentials.access_token.label('access_token'),
        DhanCredentials.user_id.label('user_id')
        ).filter(DhanCredentials.user_id == trader_id, 
    DhanCredentials.is_active == True
    ).first()


from typing import Dict, Any

def build_angelone_order(signal_data: SignalEntryRequest,transaction_list: list) -> Dict[str, Any]:
    """
    Convert SignalEntryRequest payload into AngelOne order format
    """

    # # Determine transaction type from signal
    # if signal_data.signal in ["BUY_ENTRY"]:
    #     transaction_type = "BUY"
    # elif signal_data.signal in ["SELL_ENTRY"]:
    #     transaction_type = "SELL"
    # else:
    #     raise ValueError(f"Unsupported signal for entry order: {signal_data.signal}")

    strike = signal_data.strike_data  # nested object

    order_params = {
        "variety": "NORMAL",
        "tradingsymbol": strike.symbol,      # <-- from StrikeData
        "symboltoken": strike.token,        # <-- from StrikeData
        "transactiontype": "BUY" if signal_data.signal.lower() in transaction_list else 'SELL',
        "exchange": strike.exchange,        # <-- from StrikeData
        "ordertype": "MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "0",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": signal_data.quantity               # your calculated qty
    }

    return order_params





def place_angelone_order(smart_api_obj, signal_data,transaction_list: list):
    order_params = build_angelone_order(signal_data,transaction_list)
    response = smart_api_obj.placeOrder(order_params)
    print("Order Response:", response)
    return response




def smartapi_login(api_key: str, username: str, password: str, totp_token: str):
    obj = SmartConnect(api_key=api_key)

    totp = pyotp.TOTP(totp_token).now()
    data = obj.generateSession(username, password, totp)

    auth_token = data['data']['jwtToken']
    feed_token = data['data']['feedToken']
    refresh_token = data['data']['refreshToken']

    print("Login Successful ✅")
    return obj

    

def get_angelone_credentials(trader_id: int, db: Session) -> dict | None:
    row = (
        db.query(
            AngelOneCredentials.username.label("username"),
            AngelOneCredentials.token.label("access_token"),
            AngelOneCredentials.api_key.label("api_key"),
            AngelOneCredentials.password.label("password"),
        )
        .filter(
            AngelOneCredentials.user_id == trader_id,
            AngelOneCredentials.is_active == True
        )
        .first()
    )

    if not row:
        return None

    return {
        "username": row.username,
        "access_token": row.access_token,
        "api_key": row.api_key,
        "password": row.password,
    }



def handle_order(trader_id: int, signal_log_id: int, strike_data, signal_data, transaction_list: list, db: Session, strategy_id: int = 1):
    """
    Handle order placement and closure based on trading signals.

    Parameters:
        trader_id (int): The ID of the trader.
        signal_log_id (int): The signal log ID.
        strike_data: Object containing `symbol`, `position`, and `lot_qty`.
        signal_data: Object containing `signal` attribute.
        transaction_list (list): List of active signals to trigger orders.
        db (Session): SQLAlchemy session.
        strategy_id (int): Strategy ID for the order. Default is 1.
    """

    # Check if signal matches the allowed transaction list
    if signal_data.signal.lower() in transaction_list:
        # Log the order
        with open('order_log.txt', 'a') as f:
            f.write(
                f'trader_id: {trader_id}, signal_log_id: {signal_log_id}, '
                f'symbol: {strike_data.symbol}, position: {strike_data.position}, '
                f'lot_qty: {strike_data.lot_qty}\n'
            )

        time.sleep(5)
        print('Adding order to db')

        # Fetch latest LTP
        ltp = (
            db.query(StrikePriceTickData.ltp)
            .filter(StrikePriceTickData.symbol == strike_data.symbol)
            .order_by(StrikePriceTickData.id.desc())
            .limit(1)
            .scalar()
        )

        # Add new order
        db.add(
            Order(
                strategy_id=strategy_id,
                user_id=trader_id,
                signal_log_id=signal_log_id,
                symbol=strike_data.symbol,
                option_type=strike_data.position,
                qty=strike_data.lot_qty,
                entry_price=float(ltp) if ltp is not None else 0.0,
                status="OPEN",
                entry_time=datetime.now(ZoneInfo("Asia/Kolkata")),
                is_deleted=False
            )
        )
        db.commit()
        print('Order added to db')

    else:
        # Close any open order for this signal
        open_order = (
            db.query(Order)
            .filter(
                Order.user_id == trader_id,
                Order.signal_log_id == signal_log_id,
                Order.status == "OPEN"
            )
            .first()
        )

        if open_order:
            open_order.status = "CLOSED"

            # Fetch latest LTP for exit price
            exit_ltp = (
                db.query(StrikePriceTickData.ltp)
                .filter(StrikePriceTickData.symbol == strike_data.symbol)
                .order_by(StrikePriceTickData.id.desc())
                .limit(1)
                .scalar()
            )

            open_order.exit_price = float(exit_ltp) if exit_ltp is not None else 0.0
            open_order.exit_time = datetime.now(ZoneInfo("Asia/Kolkata"))

            db.commit()
            print(f"Closed order for symbol {strike_data.symbol}, trader_id {trader_id}")



def call_broker_api(trader_id: int,signal_log_id: int, signal_data, db: Session=None):
    from app.db.db import SessionLocal
    db = SessionLocal()
    print(f'Placing order for trader_id: {trader_id}, signal_log_id: {signal_log_id}')
    strike_data = signal_data.strike_data
    dhan_creds=get_dhan_credentials(trader_id=trader_id, db=db)
    angelone_creds=get_angelone_credentials(trader_id=trader_id, db=db)
    # if not dhan_creds:
    #     return False
    print('Dhan Credentials:', dhan_creds.client_id,dhan_creds.access_token,dhan_creds.user_id)
    transaction_list = ['buy_entry','sell_entry']
    
    if dhan_creds:
        # dhan_context=DhanContext(client_id=dhan_creds['client_id'], access_token=dhan_creds['access_token'])
        try:
            dhan_context = DhanContext(client_id=dhan_creds.client_id, access_token=dhan_creds.access_token)

            dhan = dhanhq(dhan_context)
            exchange_segment = (
                dhan.NSE_FNO if strike_data.exchange == 'NSE_FNO'
                else dhan.BSE_FNO if strike_data.exchange == 'BSE_FNO'
                else dhan.NSE_FNO
            )
            dhan_res = dhan.place_order(
            security_id=strike_data.token,
            exchange_segment=exchange_segment,
            transaction_type=dhan.BUY if signal_data.signal.lower() in transaction_list else dhan.SELL,
            quantity=strike_data.lot_qty,
            order_type=dhan.MARKET,
            product_type=dhan.INTRA,
            price=0,
            )
            print('Dhan Response:', dhan_res)
        except Exception as e:
            print('Dhan Error:', e)
        print('signal if ',signal_data.signal)
        if signal_data.signal.lower() in transaction_list:
            with open('order_log.txt', 'a') as f:
                f.write(f'trader_id: {trader_id}, signal_log_id: {signal_log_id}, symbol: {strike_data.symbol}, position: {strike_data.position}, lot_qty: {strike_data.lot_qty}\n')
            time.sleep(5)   
            print('Adding order to db')
            ltp = (
                db.query(StrikePriceTickData.ltp)
                .filter(StrikePriceTickData.symbol == strike_data.symbol)
                .order_by(StrikePriceTickData.id.desc()).limit(1)
                .scalar()
            )
            db.add(
            Order(
                strategy_id=1,
                user_id=trader_id,
                signal_log_id=signal_log_id,
                symbol=strike_data.symbol,
                option_type=strike_data.position,
                qty=strike_data.lot_qty,
                entry_price=float(ltp) if ltp is not None else 0.0,
                status="OPEN",
                entry_time=datetime.now(ZoneInfo("Asia/Kolkata")),
                is_deleted=False
            )
            )
            db.commit()
            print('Order added to db')
        
        else:
            #get open order from orders table for the particular trader_id and signal_log_id
            open_order = db.query(Order).filter(Order.user_id == trader_id, Order.signal_log_id == signal_log_id, Order.status == "OPEN").first()
            print('order check point 1',open_order.user_id)
            if open_order:
                open_order.status = "CLOSED"

                open_order.exit_price = (
                    db.query(StrikePriceTickData.ltp)
                    .filter(StrikePriceTickData.symbol == strike_data.symbol)
                    .order_by(StrikePriceTickData.id.desc()).limit(1)
                    .scalar()
                ) or 0

                open_order.exit_time = datetime.now(ZoneInfo("Asia/Kolkata"))
                db.commit()


    if angelone_creds:
        try:
            smart_api = smartapi_login(
                api_key=angelone_creds["api_key"],
                username=angelone_creds["username"],
                password=angelone_creds["password"],
                totp_token=angelone_creds["totp_token"],
            )

            place_angelone_order(smart_api_obj=smart_api, 
                                signal_data=signal_data,
                                transaction_list=transaction_list)
                
        except Exception as e:
            print('AngelOne Error:', e)
            raise 'AngelOne Error '+str(e)
        handle_order(
                        trader_id=trader_id, 
                        signal_log_id=signal_log_id, 
                        strike_data=strike_data, 
                        signal_data=signal_data, 
                        transaction_list=transaction_list, 
                        strategy_id=1,
                        db=db)




