from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.models import User, Order,StrikePriceTickData


from pydantic import BaseModel
from datetime import datetime

class OrderResponse(BaseModel):
    id: int
    user_id: int
    symbol: str
    index: str | None
    strike: int | None
    type: str
    qty: int
    entry_price: float | None
    current_price: float | None
    pnl: float
    pnl_percent: float
    status: str
    strategy: str | None
    timestamp: datetime
    created_at: datetime
    updated_at: datetime





def get_today_trades_service(user: User, db: Session):
    try:
        today = datetime.now().date()

        orders = (
            db.query(Order)
            .filter(Order.user_id == user.id)
            .filter(func.date(Order.entry_time) == today)
            .filter(Order.is_deleted.is_(False))
            .all()
        )

        orders_list = []

        for order in orders:
            print('order.status is :: ',order.status)

            # 🔹 Get current price
            if order.status == "OPEN":
                tick = (
                    db.query(StrikePriceTickData.ltp)
                    .filter(StrikePriceTickData.symbol == order.symbol)
                    .order_by(StrikePriceTickData.id.desc())
                    .first()
                )
                current_price = tick[0] if tick else 0
            else:
                current_price = order.exit_price

            pnl = (current_price - order.entry_price) * order.qty
            # pnl_percent = (pnl / (order.entry_price * order.qty)) * 100
            print('current_price is :: ',current_price)
            print('order.entry_price is :: ',order.entry_price)
            print('order.qty is :: ',order.qty)
            print('pnl is :: ',pnl)
            # print('pnl_percent is :: ',pnl_percent)
            response = OrderResponse(
                id=order.id,
                user_id=order.user_id,
                symbol=order.symbol,
                index=None,                 # ❗ not in model
                strike=None,                # ❗ not in model
                type=order.option_type,     # ✅ correct mapping
                qty=order.qty,
                entry_price=float(order.entry_price) if order.entry_price else None,
                current_price=float(current_price) if current_price else 0,
                # pnl=float(order.pnl) if order.pnl else 0.0,
                pnl = pnl,
                # pnl_percent=float(order.pnl_percent) if order.pnl_percent else 0.0,
                pnl_percent = (pnl / (order.entry_price * order.qty)) * 100,
                status=order.status,
                strategy=order.strategy.name if order.strategy else None,
                timestamp=order.entry_time,     # using entry_time
                created_at=order.entry_time,    # if no separate column
                updated_at=order.entry_time      # fallback
            )

            orders_list.append(response)

        return orders_list
    except Exception as e:
        # logger.error(f"Error getting trades: {str(e)}")
        print('Error getting trades: ',str(e))
        # raise HTTPException(
        #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     detail="Error retrieving trades"
        # )
