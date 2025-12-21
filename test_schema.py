import sys
import os
from pydantic import ValidationError

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.schemas.signal_schema import SignalEntryRequest

sample_payload = {
  "token": "string",
  "signal": "string",
  "unique_id": "string",
  "strategy_code": "string",
  "strike_data": {
      "token": 35000,
      "exchange": "OPTIDX",
      "index_name": "BANKNIFTY",
      "DOE": "2025-12-30 00:00:00", # Stringified Timestamp for Pydantic
      "strike_price": 69700,
      "position": "CE",
      "symbol": "BANKNIFTY-Dec2025-69700-CE"
  }
}

try:
    signal = SignalEntryRequest(**sample_payload)
    print("Schema Validation Successful!")
    print(f"Token: {signal.token} (Type: {type(signal.token).__name__})")
    print(f"Strike Token: {signal.strike_data.token} (Type: {type(signal.strike_data.token).__name__})")
    print(f"Strike Symbol: {signal.strike_data.symbol}")
except ValidationError as e:
    print("Schema Validation Failed!")
    print(e.json())
except Exception as e:
    print(f"An error occurred: {e}")
