from app.db.db import SessionLocal
from app.models.models import SignalLog, Order
from sqlalchemy import func

db = SessionLocal()
try:
    total_signals = db.query(func.count(SignalLog.id)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()
    
    print(f"Total SignalLogs: {total_signals}")
    print(f"Total Orders: {total_orders}")

    latest_orders = db.query(Order).order_by(Order.id.desc()).limit(5).all()
    print("\nLatest 5 Orders:")
    for o in latest_orders:
        print(f"ID: {o.id}, Symbol: {o.symbol}, Qty: {o.qty}, Entry: {o.entry_price}, Exit: {o.exit_price}")

finally:
    db.close()
