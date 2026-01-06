from dhanhq import DhanContext, MarketFeed
import json
from datetime import date, datetime, timedelta
import time
import requests

import pytz
ist = pytz.timezone("Asia/Kolkata")

client_id = '1100465668' #raja sir id
access_token ='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzY3NzU5NjUzLCJpYXQiOjE3Njc2NzMyNTMsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTAwNDY1NjY4In0.VD94mxWH_iI2A0AzfKVI-7OA9QisCEdZqkqrtC5vhe8MMnuLK4Qt5RwIO2c2-gEDMCK24bCGLSVefY2n6HUpsw'

# client_id = '1100449732'   # Divya ID
# access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzY3NzYxMzk2LCJpYXQiOjE3Njc2NzQ5OTYsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTAwNDQ5NzMyIn0.xYRXr46pwv7zuGql5BNCf13gQwhpzNKJwD5VoT_XrYjY4CdAoFM5a8a-PQ2RxKwrwoUE4MwL19P6VEFVqoFFFQ"

marketfeed_dict = {
    'MCX': MarketFeed.MCX,
    'NSE': MarketFeed.NSE,
    'BSE': MarketFeed.BSE,
    'BSE_FNO':MarketFeed.BSE_FNO,
    'NSE_FNO':MarketFeed.NSE_FNO,
    'IDX':MarketFeed.IDX,

}

global_secid_symbol_mapper_dict = {
    '25':'BANKNIFTY-TEST',
    '464925':'CRUDEOIL-TEST'
}



def get_new_strike_instruments():
    url = "http://localhost:8000/api/tick/get-active-strike-instruments"

    resp = requests.get(url)
    resp.raise_for_status()

    payload = resp.json()          # ✅ parse JSON
    records = payload.get("data", [])

    instruments = []

    for rec in records:
        token = rec["token"]
        symbol = rec["symbol"]
        exchange = rec["exchange"]

        global_secid_symbol_mapper_dict[token] = symbol

        instruments.append(
            (marketfeed_dict[exchange], token, MarketFeed.Ticker)
        )
    print('global_secid_symbol_mapper_dict : ',global_secid_symbol_mapper_dict)
    return instruments






def insert_spot_ltp_api(token:str,ltp:float,):
    url = "http://localhost:8000/api/tick/insert-strike-ltp"
    data = {
        "token": token,
        "ltp": ltp,
        'symbol': global_secid_symbol_mapper_dict[token]
    }
    response = requests.post(url, json=data)
    return response.json()




dhan_context = DhanContext(client_id, access_token)

instruments = [
    (MarketFeed.MCX, '464925', MarketFeed.Ticker),
    (MarketFeed.MCX, '486533', MarketFeed.Ticker),
    (MarketFeed.IDX, "25", MarketFeed.Ticker)
]

version = "v2"



print(instruments)

retry_delay = 5
max_retry_delay = 60
retry_count = 0


while True:
    try:
        data = MarketFeed(dhan_context, instruments, version)
        print("Starting Market Feed...")
        retry_delay = 5
        retry_count = 0
        while True:
            now_ist = datetime.now(ist)
            start_time = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
            end_time = now_ist.replace(hour=23, minute=30, second=0, microsecond=0)
            sub_instruement = get_new_strike_instruments()
            print("sub_instruement : ",sub_instruement)
            if sub_instruement :
                data.subscribe_symbols(sub_instruement)
            
            # print(now_ist)

            if not (start_time <= now_ist <= end_time):
                print("📈 Waiting for Market Hours (9:15 AM – 3:30 PM)...")
                # time.sleep(60)
                continue

            data.run_forever()
            response = data.get_data()
            print(f"Response: {response}")

            if 'LTP' not in response or 'LTT' not in response:
                print(f"Missing data for token , response: {response}")
                continue

            ltp = response['LTP']
            ltt_time_str = response['LTT']  # "HH:MM:SS"

            # --- TICK TIMESTAMP FIX (FINAL SOLUTION) ---

            # Parse tick time
            tick_time = datetime.strptime(ltt_time_str, "%H:%M:%S").time()

            # Get today’s date from IST clock
            tick_date = now_ist.date()

            # Combine date + tick time
            ts = datetime.combine(tick_date, tick_time).astimezone(ist)

            # Insert spot LTP
            try:
                insert_spot_ltp_api(
                    token=str(response['security_id']),
                    ltp=ltp,
                )
            except Exception as e:
                print(f"Spot LTP insert error: {e}")

            # Determine the candle interval
            # print(f"Tick TS: {ts}, Interval Start: {interval_start}")

    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        break

    except Exception as e:
        retry_count += 1
        print(f"❌ Main Loop Error: {e}")
        print(f"⏳ Waiting {retry_delay} seconds...")

        # time.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, max_retry_delay)
        continue
