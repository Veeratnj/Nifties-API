from dhanhq import DhanContext, MarketFeed
from datetime import datetime
import time
import requests
import pytz
import signal
import asyncio

# ================== FIX FOR PYTHON 3.11 ==================
# Create ONE persistent global event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# ================== CONFIG ==================

ist = pytz.timezone("Asia/Kolkata")

shutdown_flag = False
current_cred_index = 0
version = "v2"

global_secid_symbol_mapper_dict = {}

marketfeed_dict = {
    'MCX': MarketFeed.MCX,
    'NSE': MarketFeed.NSE,
    'BSE': MarketFeed.BSE,
    'BSE_FNO': MarketFeed.BSE_FNO,
    'NSE_FNO': MarketFeed.NSE_FNO,
    'IDX': MarketFeed.IDX,
}

# ================== SIGNAL HANDLER ==================

def signal_handler(signum, frame):
    global shutdown_flag
    print("\n" + "=" * 70)
    print("🛑 SHUTDOWN REQUESTED")
    print("=" * 70)
    shutdown_flag = True

signal.signal(signal.SIGINT, signal_handler)

# ================== CREDENTIALS ==================

def get_dhan_creds(id=2):
    try:
        url = f"http://localhost:8000/db/signals/get-admin-dhan-creds/{id}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()

        records = resp.json()
        records['client_id'] = str(records.get('client_id', '')).strip()
        records['access_token'] = records.get('access_token', '').strip()

        print(f"✅ Fetched credentials for Client ID: {records['client_id']}")
        return records

    except Exception as e:
        print(f"❌ Credential error: {e}")
        return {'client_id': '', 'access_token': ''}


CREDENTIALS = [get_dhan_creds(), get_dhan_creds()]

# ================== API HELPERS ==================

def get_new_strike_instruments():
    try:
        url = "http://localhost:8000/api/tick/get-active-strike-instruments"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()

        records = resp.json().get("data", [])
        instruments = []

        for rec in records:
            token = str(rec["token"])
            symbol = rec["symbol"]
            exchange = rec["exchange"]

            global_secid_symbol_mapper_dict[token] = symbol
            instruments.append(
                (marketfeed_dict[exchange], token, MarketFeed.Ticker)
            )

        return instruments

    except:
        return []


def insert_spot_ltp_api(token, ltp):
    try:
        url = "http://localhost:8000/api/tick/insert-strike-ltp"
        payload = {
            "token": str(token),
            "ltp": float(ltp),
            "symbol": global_secid_symbol_mapper_dict.get(token, token)
        }
        print("✅ Inserting payload", payload)
        requests.post(url, json=payload, timeout=3)
    except:
        pass


# ================== WS HELPERS ==================

def start_ws(instruments, cred_index):
    cred = CREDENTIALS[cred_index]
    ctx = DhanContext(cred['client_id'], cred['access_token'])
    ws = MarketFeed(ctx, instruments, version)
    print(f"✅ WS started with Client ID: {cred['client_id']}")
    return ws


def stop_ws(ws):
    """Safe disconnect using persistent event loop"""
    try:
        loop.run_until_complete(ws.disconnect())
        print("🛑 WS disconnected")
    except Exception as e:
        print(f"⚠️ Disconnect error: {e}")


# ================== MAIN ==================

def main():
    global shutdown_flag, current_cred_index

    print("=" * 70)
    print("🚀 DHAN MARKET FEED STARTING")
    print("=" * 70)

    instruments = [
        (MarketFeed.IDX, "25", MarketFeed.Ticker),
    ]

    ws = start_ws(instruments, current_cred_index)
    known_tokens = {i[1] for i in instruments}

    last_reload_check = 0
    reload_interval = 5
    last_tick_time = time.time()

    while not shutdown_flag:
        try:
            now_ist = datetime.now(ist)

            start_time = now_ist.replace(hour=9, minute=0, second=0)
            end_time = now_ist.replace(hour=23, minute=30, second=0)

            if not (start_time <= now_ist <= end_time):
                time.sleep(5)
                continue

            current_time = time.time()

            # 🔁 Check new instruments
            if current_time - last_reload_check > reload_interval:
                new_instruments = get_new_strike_instruments()
                new_tokens = {i[1] for i in new_instruments}

                if new_tokens and not new_tokens.issubset(known_tokens):
                    print("♻ Restarting WS with new instruments")
                    known_tokens.update(new_tokens)

                    instruments += new_instruments
                    stop_ws(ws)
                    time.sleep(1)
                    ws = start_ws(instruments, current_cred_index)

                last_reload_check = current_time

            # 🔌 Run WebSocket
            ws.run_forever()
            response = ws.get_data()

            if not response:
                if current_time - last_tick_time > 60:
                    raise Exception("No ticks received")
                continue

            last_tick_time = current_time

            if 'LTP' in response and 'security_id' in response:
                print("✅ Inserting LTP", response)
                insert_spot_ltp_api(
                    token=response['security_id'],
                    ltp=response['LTP']
                )

        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Rotating credentials...")

            current_cred_index = (current_cred_index + 1) % len(CREDENTIALS)

            stop_ws(ws)
            time.sleep(5)
            ws = start_ws(instruments, current_cred_index)

    # Final cleanup
    stop_ws(ws)
    print("✅ Program ended gracefully")


if __name__ == "__main__":
    main()