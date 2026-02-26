from dhanhq import DhanContext, MarketFeed
from datetime import datetime
import time
import requests
import pytz
import sys
import signal
import asyncio   # ✅ ADDED

# ================== CONFIG ==================

ist = pytz.timezone("Asia/Kolkata")

# ================== CREDENTIALS ==================

def get_dhan_creds(id=2):
    try:
        url = f"http://localhost:8000/db/signals/get-admin-dhan-creds/{str(id)}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()

        records = resp.json()

        if isinstance(records, dict):
            records['client_id'] = str(records.get('client_id', '')).strip()
            records['access_token'] = records.get('access_token', '').strip()

        print(f"✅ Fetched credentials for Client ID: {records.get('client_id', 'Unknown')}")
        return records

    except Exception as e:
        print(f"❌ Error fetching credentials: {e}")
        return {'client_id': '', 'access_token': ''}


CREDENTIALS = [get_dhan_creds(), get_dhan_creds()]
current_cred_index = 0

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

shutdown_flag = False

# ================== SIGNAL HANDLER ==================

def signal_handler(signum, frame):
    global shutdown_flag
    print("\n\n" + "=" * 70)
    print("🛑 SHUTDOWN REQUESTED")
    print("=" * 70)
    shutdown_flag = True   # ❗ DO NOT sys.exit() here


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

    except Exception as e:
        print(f"⚠️ Instrument fetch error: {e}")
        return []


def insert_spot_ltp_api(token: str, ltp: float):
    try:
        url = "http://localhost:8000/api/tick/insert-strike-ltp"
        payload = {
            "token": str(token),
            "ltp": float(ltp),
            "symbol": global_secid_symbol_mapper_dict.get(token, token)
        }
        requests.post(url, json=payload, timeout=3)
        return True
    except:
        return False


# ================== WS HELPERS ==================

def start_ws(instruments, cred_index=0):
    cred = CREDENTIALS[cred_index]

    ctx = DhanContext(cred['client_id'], cred['access_token'])
    ws = MarketFeed(ctx, instruments, version)

    print(f"✅ WS started with Client ID: {cred['client_id']}")
    return ws


def stop_ws(ws):
    """Safe async disconnect (Manual + Jenkins safe)"""
    try:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(ws.disconnect())
        except RuntimeError:
            asyncio.run(ws.disconnect())

        print("🛑 WS disconnected")

    except Exception as e:
        print(f"⚠️ Disconnect error: {e}")


# ================== MAIN ==================

def main():
    global shutdown_flag, current_cred_index

    signal.signal(signal.SIGINT, signal_handler)

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

            start_time = now_ist.replace(hour=9, minute=0, second=0, microsecond=0)
            end_time = now_ist.replace(hour=23, minute=30, second=0, microsecond=0)

            if not (start_time <= now_ist <= end_time):
                time.sleep(5)
                continue

            current_time = time.time()

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

            ws.run_forever()
            response = ws.get_data()

            if not response:
                if current_time - last_tick_time > 60:
                    raise Exception("Connection timeout")
                continue

            last_tick_time = current_time

            if 'LTP' in response and 'security_id' in response:
                insert_spot_ltp_api(
                    token=str(response['security_id']),
                    ltp=response['LTP']
                )

        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Rotating credentials...")

            current_cred_index = (current_cred_index + 1) % len(CREDENTIALS)

            try:
                stop_ws(ws)
            except:
                pass

            time.sleep(5)
            ws = start_ws(instruments, current_cred_index)

    # Final Cleanup
    try:
        stop_ws(ws)
    except:
        pass

    print("✅ Program ended gracefully")


if __name__ == "__main__":
    main()