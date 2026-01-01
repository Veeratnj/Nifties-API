
from datetime import datetime
from zoneinfo import ZoneInfo
from app.models.models import Order, User, DhanCredentials
from sqlalchemy.orm import Session
from typing import List
from dhanhq import dhanhq, DhanContext
from fastapi import Request

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
    



def call_broker_dhan_api(trader_id: int,signal_log_id: int, signal_data, db: Session):
    print(f'Placing order for trader_id: {trader_id}, signal_log_id: {signal_log_id}')
    strike_data = signal_data.strike_data
    dhan_creds=get_dhan_credentials(trader_id=trader_id, db=db)
    print('Dhan Credentials:', dhan_creds.client_id,dhan_creds.access_token,dhan_creds.user_id)
    transaction_list = ['buy_entry','sell_entry']
    if dhan_creds:
        # dhan_context=DhanContext(client_id=dhan_creds['client_id'], access_token=dhan_creds['access_token'])
        dhan_context = DhanContext(client_id=dhan_creds.client_id, access_token=dhan_creds.access_token)
        dhan = dhanhq(dhan_context)
        dhan_res = dhan.place_order(
        security_id=strike_data.token,
        exchange_segment=dhan.NSE_FNO,
        transaction_type=dhan.BUY if signal_data.signal.lower() in transaction_list else dhan.SELL,
        quantity=35,
        order_type=dhan.MARKET,
        product_type=dhan.INTRA,
        price=0,
        )
        print('Dhan Response:', dhan_res)
        if signal_data.signal.lower() in transaction_list:
            db.add(
            Order(
                user_id=trader_id,
                signal_log_id=signal_log_id,
                symbol=strike_data.symbol,
                option_type=strike_data.position,
                qty=35,
                entry_price=request.app.state.ltp.setdefault(strike_data.token, 0),
                status="OPEN",
                entry_time=datetime.now(ZoneInfo("Asia/Kolkata")),
                is_deleted=False
            )
        )
            db.commit()
        else:
            #get open order from orders table for the particular trader_id and signal_log_id
            open_order = db.query(Order).filter(Order.user_id == trader_id, Order.signal_log_id == signal_log_id, Order.status == "OPEN").first()
            if open_order:
                #update the open order status to closed
                open_order.status = "CLOSED"
                open_order.exit_time = datetime.now(ZoneInfo("Asia/Kolkata"))
                db.commit()
        




