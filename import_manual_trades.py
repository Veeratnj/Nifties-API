import pandas as pd
from datetime import datetime
from app.db.db import SessionLocal
from app.models.models import SignalLog, Order, Strategy
from zoneinfo import ZoneInfo
import sys

IST = ZoneInfo("Asia/Kolkata")

def parse_time(time_val):
    if isinstance(time_val, datetime):
        return time_val.replace(tzinfo=IST)
    # Format in CSV: 18/Dec/2025 07:43:21 PM
    try:
        return datetime.strptime(str(time_val), "%d/%b/%Y %I:%M:%S %p").replace(tzinfo=IST)
    except (ValueError, TypeError):
        # Fallback for other formats if needed
        return pd.to_datetime(time_val).to_pydatetime().replace(tzinfo=IST)

def import_trades(file, user_id=3, strategy_code="DAIKOKUTEN"):
    print(f"Starting import from {file} for user {user_id}...")
    
    # Read CSV
    try:
        df = pd.read_csv(file)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    db = SessionLocal()
    
    try:
        strategy = db.query(Strategy).filter(Strategy.name == strategy_code).first()
        strategy_id = strategy.id if strategy else None
        if not strategy_id:
            print(f"Warning: Strategy {strategy_code} not found. Continuing without strategy_id.")
        
        for index, row in df.iterrows():
            try:
                symbol = row['SYMBOL']
                order_type = row['ORDER'].upper()
                # Clean quantity (remove commas, handle potential floats/strings)
                qty_str = str(row['QUANTITY']).replace(',', '')
                qty = int(float(qty_str)) 
                
                # Prices
                entry_price = float(str(row['BUY ENTRY']).replace(',', ''))
                exit_price = float(str(row['SELL ENTRY']).replace(',', ''))
                
                # Times
                entry_time = parse_time(row['ENTRY TIME'])
                exit_time = parse_time(row['EXIT TIME'])
                
                # Use string symbol for unique_id
                unique_id = f"MANUAL_IMPORT_{int(entry_time.timestamp())}_{index}"
                
                print(f"Processing {symbol}...")

                # 1. Create Entry Signal Log
                entry_signal = SignalLog(
                    token=symbol.split('-')[0], # Base symbol
                    signal_type=f"{order_type}_ENTRY",
                    unique_id=unique_id,
                    strike_price_token=symbol, # Full symbol as strike token
                    strategy_code=strategy_code,
                    signal_category="ENTRY",
                    timestamp=entry_time
                )
                db.add(entry_signal)
                db.flush()
                
                # 2. Create Exit Signal Log
                exit_signal = SignalLog(
                    token=symbol.split('-')[0],
                    signal_type=f"{order_type}_EXIT",
                    unique_id=unique_id,
                    strike_price_token=symbol,
                    strategy_code=strategy_code,
                    signal_category="EXIT",
                    timestamp=exit_time
                )
                db.add(exit_signal)
                db.flush()
                
                # 3. Create Order
                order = Order(
                    user_id=user_id,
                    signal_log_id=entry_signal.id,
                    strategy_id=strategy_id,
                    symbol=symbol,
                    option_type="CE" if "CE" in symbol else "PE",
                    qty=qty,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    status="CLOSED",
                    entry_time=entry_time,
                    exit_time=exit_time,
                    is_deleted=False
                )
                db.add(order)
                
            except Exception as row_error:
                print(f"Error processing row {index}: {row_error}")
                continue
            
        print(f"Successfully staged trades for import.")
        db.commit()
        print("Import completed successfully.")
        
    except Exception as e:
        db.rollback()
        print(f"Critical error during import: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_trades("30.12.25.csv")
