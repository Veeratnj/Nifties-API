from dhanhq import DhanContext, MarketFeed
from datetime import datetime
import time
import requests
import pytz
import sys
import signal

# ================== CONFIG ==================

ist = pytz.timezone("Asia/Kolkata")

client_id = '1100465668' #raja sir id
access_token ='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzY5MDE0MjU4LCJpYXQiOjE3Njg5Mjc4NTgsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTAwNDY1NjY4In0.SNg2dBSlBq5-YxVoJO2phXcHbLGhdbEZhZPxTihee9m5QaxLEt9Nm6w9gJbaqpFrEuy0z4lo7bPjQTpJ4tnjIw'

# client_id = '1100449732' #divya sir id
# access_token ='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzY5MDE0MTczLCJpYXQiOjE3Njg5Mjc3NzMsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTAwNDQ5NzMyIn0.efaEyCbDWot2WEgFOeVZJj6Z_2leJAWcI7O9PHTzJToOk2W7LYy4IwOS4Cv3KR28fI9GWwvH2jdh43KPi20aQw'




version = "v2"

marketfeed_dict = {
    'MCX': MarketFeed.MCX,
    'NSE': MarketFeed.NSE,
    'BSE': MarketFeed.BSE,
    'BSE_FNO': MarketFeed.BSE_FNO,
    'NSE_FNO': MarketFeed.NSE_FNO,
    'IDX': MarketFeed.IDX,
}

global_secid_symbol_mapper_dict = {}

# Graceful shutdown flag
shutdown_flag = False

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    global shutdown_flag
    print("\n\n" + "=" * 70)
    print("🛑 SHUTDOWN REQUESTED")
    print("=" * 70)
    shutdown_flag = True
    sys.exit(0)

# ================== API HELPERS ==================

def get_new_strike_instruments():
    """Fetch active strike instruments from API"""
    try:
        url = "http://localhost:8000/api/tick/get-active-strike-instruments"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()

        records = resp.json().get("data", [])
        instruments = []

        for rec in records:
            token = str(rec["token"])  # Ensure token is string
            symbol = rec["symbol"]
            exchange = rec["exchange"]

            global_secid_symbol_mapper_dict[token] = symbol
            instruments.append(
                (marketfeed_dict[exchange], token, MarketFeed.Ticker)
            )

        return instruments
        
    except requests.exceptions.ConnectionError:
        print("⚠️ API not reachable (expected if no new instruments)")
        return []
    except requests.exceptions.Timeout:
        print("⚠️ API request timeout")
        return []
    except Exception as e:
        print(f"❌ Error fetching instruments: {e}")
        return []


def insert_spot_ltp_api(token: str, ltp: float):
    """Insert LTP data via API"""
    try:
        url = "http://localhost:8000/api/tick/insert-strike-ltp"
        payload = {
            "token": str(token),
            "ltp": float(ltp),
            "symbol": global_secid_symbol_mapper_dict.get(token, token)
        }
        response = requests.post(url, json=payload, timeout=3)
        response.raise_for_status()
        return True
    except Exception as e:
        # Don't spam logs with errors
        if hasattr(insert_spot_ltp_api, 'last_error_print'):
            if time.time() - insert_spot_ltp_api.last_error_print > 60:
                print(f"⚠️ LTP insert error: {e}")
                insert_spot_ltp_api.last_error_print = time.time()
        else:
            insert_spot_ltp_api.last_error_print = time.time()
        return False

# ================== WS HELPERS ==================

def start_ws(instruments):
    """Start WebSocket connection"""
    ctx = DhanContext(client_id, access_token)
    ws = MarketFeed(ctx, instruments, version)
    print(f"✅ WS started with {len(instruments)} instruments")
    print(f"✅ WS started with {instruments}")
    
    # Log what we're subscribing to
    if instruments:
        print("📋 Current instruments:")
        for i, (exch, token, sub_type) in enumerate(instruments[:5]):  # Show first 5
            symbol = global_secid_symbol_mapper_dict.get(token, token)
            print(f"   {i+1}. {symbol} ({token})")
        if len(instruments) > 5:
            print(f"   ... and {len(instruments) - 5} more")
    
    return ws


def stop_ws(ws):
    """Stop WebSocket connection"""
    try:
        ws.disconnect()
        print("🛑 WS disconnected")
    except Exception as e:
        print(f"⚠️ Disconnect error: {e}")

# ================== MAIN LOOP ==================

def main():
    global shutdown_flag
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 70)
    print("🚀 DHAN MARKET FEED STARTING")
    print("=" * 70)
    
    # Start with default instruments
    instruments = [
        # (MarketFeed.MCX, '464925', MarketFeed.Ticker),
        (MarketFeed.IDX, "25", MarketFeed.Ticker),
    ]
    
    # Initialize symbol mapper for defaults
    # global_secid_symbol_mapper_dict['464925'] = 'CRUDEOIL-TEST'
    # global_secid_symbol_mapper_dict['25'] = 'BANKNIFTY-TEST'
    
    ws = start_ws(instruments)
    known_tokens = {i[1] for i in instruments}
    
    last_reload_check = 0
    reload_interval = 5  # Check every 5 seconds
    tick_count = 0
    last_tick_time = time.time()
    
    try:
        while not shutdown_flag:
            now_ist = datetime.now(ist)
            
            # Market hours check - extended for MCX
            start_time = now_ist.replace(hour=9, minute=0, second=0, microsecond=0)
            end_time = now_ist.replace(hour=23, minute=0, second=0, microsecond=0)
            
            # Skip if outside market hours
            if not (start_time <= now_ist <= end_time):
                # If market closed and it's after 11 PM, wait longer
                if now_ist.hour >= 23:
                    print(f"⏰ {now_ist.strftime('%H:%M:%S')} - Market closed until 9 AM")
                    time.sleep(60)
                else:
                    time.sleep(5)
                continue
            
            # ⏱ Check for new instruments every X seconds
            current_time = time.time()
            if current_time - last_reload_check > reload_interval:
                new_instruments = get_new_strike_instruments()
                new_tokens = {i[1] for i in new_instruments}
                
                # Check if we have NEW tokens (not subset of known tokens)
                if new_tokens and not new_tokens.issubset(known_tokens):
                    print(f"\n♻ New instruments detected → Restarting WS")
                    print(f"   Old: {len(known_tokens)} instruments")
                    print(f"   New: {len(new_tokens)} instruments")
                    
                    # Add new tokens to known set
                    known_tokens.update(new_tokens)
                    
                    # Combine old and new instruments, remove duplicates
                    all_instruments = instruments + new_instruments
                    unique_instruments = []
                    seen = set()
                    for inst in all_instruments:
                        key = (inst[0], inst[1])  # (exchange, token)
                        if key not in seen:
                            seen.add(key)
                            unique_instruments.append(inst)
                    
                    # Update instruments list
                    instruments = unique_instruments
                    
                    # Restart WebSocket
                    stop_ws(ws)
                    time.sleep(1)  # Brief pause
                    ws = start_ws(instruments)
                    tick_count = 0  # Reset tick counter
                
                last_reload_check = current_time
            
            # Process WebSocket data
            ws.run_forever()
            response = ws.get_data()
            
            if response:
                tick_count += 1
                last_tick_time = current_time
                
                # Print progress every 100 ticks
                if tick_count % 100 == 0:
                    now_time = datetime.now(ist).strftime("%H:%M:%S")
                    print(f"📈 [{now_time}] Processed {tick_count} ticks")
            
            if not response or 'LTP' not in response or 'security_id' not in response:
                continue

            # Process the tick
            try:
                insert_spot_ltp_api(
                    token=str(response['security_id']),
                    ltp=response['LTP']
                )
            except Exception as e:
                print(f"Insert error: {e}")
            
            # Check for connection timeout (no ticks for 30 seconds)
            if current_time - last_tick_time > 30:
                print("⚠️ No ticks received for 30 seconds - forcing refresh...")
                last_reload_check = 0  # Force check on next iteration

    except KeyboardInterrupt:
        print("\n🛑 Keyboard Interrupt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        stop_ws(ws)
        print("\n✅ Program ended gracefully")


if __name__ == "__main__":
    main()