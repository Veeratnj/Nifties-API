import logging
import asyncio
from dhanhq import MarketFeed , DhanContext
from typing import Callable

logger = logging.getLogger(__name__)



def start_ltp_websocket(token: str, app, callback=None):
    """
    Start MarketFeed WebSocket for a token.
    DhanContext is created inside.
    LTP is stored in app.state.ltp[token], or 0 on error.
    """
    # try:
    #     # --- Initialize DhanContext ---
    #     dhan_context = DhanContext('1100465668', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzY3MzI1MjY1LCJpYXQiOjE3NjcyMzg4NjUsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTAwNDY1NjY4In0.ut8FQnXZQh-tJkdBKHfx6T6yTyIwo6oAcN3AWSdgshxj0tprWS2ovzBryK9Vbv7FI4v3dPmDUciRXryy3PbAdA')

    #     instruments = [(MarketFeed.NSE_FNO, token, MarketFeed.Ticker)]
    #     version = "v2"
    #     data = MarketFeed(dhan_context, instruments, version)

    #     logger.info(f"📡 LTP WS started for token {token}")

    #     # Ensure LTP storage exists
    #     if not hasattr(app.state, "ltp"):
    #         app.state.ltp = {}

    #     try:
    #         while True:
    #             try:
    #                 data.run_forever()
    #                 response = data.get_data()

    #                 # If LTP missing, insert 0
    #                 ltp = float(response.get('LTP', 0)) if response else 0
    #                 print(ltp,'ltp price is qwerty')
    #                 # Store LTP
    #                 app.state.ltp[token] = ltp

    #                 # Optional callback
    #                 if callback:
    #                     callback(token, ltp)

    #             except Exception as e:
    #                 logger.warning(f"⚠️ Error fetching LTP for {token}: {e}. Setting LTP=0")
    #                 app.state.ltp[token] = 0
    #                 if callback:
    #                     callback(token, 0)
    #                 # Wait a bit before retrying
    #                 asyncio.sleep(1)

    #     except Exception as e:
    #         logger.exception(f"❌ LTP WS error for token {token}: {e}")

    #     finally:
    #         try:
    #             data.close()
    #         except Exception:
    #             pass
    #         logger.info(f"🔒 LTP WS closed for token {token}")
    # except Exception as e:
    #     print('erreor is :',e)
    #     logger.exception(f"❌ LTP WS error for token {token}: {e}")


async def get_ltp(app, token: str):
    """
    Safely read LTP from app.state
    """
    ltp = app.state.ltp.get(token)
    return ltp  # returns None if not found
