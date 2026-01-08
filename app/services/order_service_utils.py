
from datetime import datetime
from zoneinfo import ZoneInfo
from app.models.models import Order, User, DhanCredentials , StrikePriceTickData
from sqlalchemy.orm import Session
from typing import List
from dhanhq import dhanhq, DhanContext
from fastapi import Request
import time

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
    



def call_broker_dhan_api(trader_id: int,signal_log_id: int, signal_data, db: Session=None):
    from app.db.db import SessionLocal
    db = SessionLocal()
    print(f'Placing order for trader_id: {trader_id}, signal_log_id: {signal_log_id}')
    strike_data = signal_data.strike_data
    dhan_creds=get_dhan_credentials(trader_id=trader_id, db=db)
    print('Dhan Credentials:', dhan_creds.client_id,dhan_creds.access_token,dhan_creds.user_id)
    transaction_list = ['buy_entry','sell_entry']
    if dhan_creds:
        # dhan_context=DhanContext(client_id=dhan_creds['client_id'], access_token=dhan_creds['access_token'])
        try:
            dhan_context = DhanContext(client_id=dhan_creds.client_id, access_token=dhan_creds.access_token)
            dhan = dhanhq(dhan_context)
            dhan_res = dhan.place_order(
            security_id=strike_data.token,
            exchange_segment=dhan.NSE_FNO,
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
            db.add(
            Order(
                strategy_id=1,
                user_id=trader_id,
                signal_log_id=signal_log_id,
                symbol=strike_data.symbol,
                option_type=strike_data.position,
                qty=strike_data.lot_qty,
                entry_price=
                    (
                        db.query(StrikePriceTickData.ltp)
                        .filter(StrikePriceTickData.symbol == strike_data.symbol)
                        .order_by(StrikePriceTickData.id.desc())
                        .limit(1)
                        .scalar()
                    ) or 0,
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
                    .order_by(StrikePriceTickData.id.desc())
                    .scalar()
                ) or 0

                open_order.exit_time = datetime.now(ZoneInfo("Asia/Kolkata"))
                db.commit()

        




