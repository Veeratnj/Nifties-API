
from datetime import datetime
from zoneinfo import ZoneInfo
from app.models.models import Order, User, DhanCredentials
from sqlalchemy.orm import Session
from typing import List
from dhanhq import dhanhq, DhanContext

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
    dhan_creds=get_dhan_credentials(trader_id=trader_id, db=db)
    if dhan_creds:
        # dhan_context=DhanContext(client_id=dhan_creds['client_id'], access_token=dhan_creds['access_token'])
        dhan_context = DhanContext(client_id=dhan_creds.client_id, access_token=dhan_creds.access_token)
        dhan = dhanhq(dhan_context)
        dhan_res = dhan.place_order(
        security_id=signal_data.token,
        exchange_segment=dhan.NSE_FNO,
        transaction_type=dhan.BUY if signal_data.signal.lower() == 'buy_entry' else dhan.SELL,
        quantity=35,
        order_type=dhan.MARKET,
        product_type=dhan.INTRA,
        price=0,
        )
        print('Dhan Response:', dhan_res)
        db.add(
            Order(
                user_id=trader_id,
                signal_log_id=signal_log_id,
                symbol=signal_data.strike_price_token,
                option_type="CE",
                qty=35,
                entry_price=0,
                status="OPEN",
                entry_time=datetime.now(ZoneInfo("Asia/Kolkata")),
                is_deleted=False
            )
        )
        db.commit()
        




