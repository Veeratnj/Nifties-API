
from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.services.market_services import MarketService
from app.schemas.schema import MarketIndexSchema, PnLSchema
from app.models.models import HistoricalData, SpotTickData, SymbolMaster
import pandas as pd

from datetime import timezone, timedelta
IST = timezone(timedelta(hours=5, minutes=30))

router = APIRouter(prefix="/db", tags=["nifties-opt"])

# 1. Get Nifty Tokens
@router.get("/indices/nifty-tokens")
def get_nifty_tokens(db: Session = Depends(get_db)):
    # Example: Return all unique index names from MarketIndex
    try:
        indices = MarketService.get_all_indices(db)
        tokens = [idx.token for idx in indices]
        return {"tokens": tokens}
    except Exception as e:
        print('e:::',e)
        raise HTTPException(status_code=500, detail=str(e))

# 2. Fetch OHLC Data
@router.get("/current/ohlc")
def fetch_current_ohlc(token: str, db: Session = Depends(get_db)):
    try:
        print("token:::", token)

        # fetch the most recent candle
        idx = (
            db.query(HistoricalData)
            .filter(HistoricalData.symbol == token)
            .order_by(HistoricalData.timestamp.desc())
            .first()
        )

        print("indices:::", idx)

        if not idx:
            return {"status": "error", "message": "No data found"}

        data = {
            "start_time": str(idx.timestamp.astimezone(IST).isoformat()),
            "open": float(idx.open),
            "high": float(idx.high),
            "low": float(idx.low),
            "close": float(idx.close)
        }

        return {"status": "success", "data": data}

    except Exception as e:
        print("e:::", e)
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/historical/ohlc/load/v1")
def load_historical_ohlc_v1(
    token: str,
    db: Session = Depends(get_db)
):
    try:
        # each day = 125 candles (3-minute)
        candles_per_day = 125
        last_n_days = 3
        total_candles = candles_per_day * last_n_days  # 375 candles
        print('total_candles:::',total_candles)
        # fetch last 375 candles
        candles = (
            db.query(HistoricalData)
            .filter(
                HistoricalData.symbol == token,
                # HistoricalData.timeframe == TimeFrame.MIN_3
            )
            .order_by(HistoricalData.timestamp.desc())
            .limit(total_candles)
            .all()
        )
        print('candles:::',candles)

        # reverse to ascending order
        candles = list(reversed(candles))

        # convert to DataFrame
        df = pd.DataFrame([{
            "timestamp": c.timestamp,
            "open": float(c.open),
            "high": float(c.high),
            "low": float(c.low),
            "close": float(c.close),
            "volume": c.volume,
        } for c in candles])

        # return DataFrame as JSON
        return {
            "symbol": token,
            "rows": len(df),
            "data": df.to_dict(orient="records")  # clean JSON format
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/historical/ohlc/load")
def load_historical_ohlc(
    token: str,
    db: Session = Depends(get_db)
):
    try:
        candles_per_day = 125
        last_n_days = 3
        total_candles = candles_per_day * last_n_days

        candles = (
            db.query(HistoricalData)
            .filter(HistoricalData.symbol == token)
            .order_by(HistoricalData.timestamp.desc())
            .limit(total_candles)
            .all()
        )

        candles = list(reversed(candles))

        df = pd.DataFrame([{
            "timestamp": c.timestamp.astimezone(IST).isoformat(),  # FIXED: IST
            "open": float(c.open),
            "high": float(c.high),
            "low": float(c.low),
            "close": float(c.close),
            "volume": c.volume,
        } for c in candles])

        return {
            "symbol": token,
            "rows": len(df),
            "data": df.to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# 3. Fetch Latest LTP
# @router.post("/indices/ltp")
# def fetch_ltp(stock_token: str = Body(...), db: Session = Depends(get_db)):
#     try:
#         print('stock_token:::',stock_token)
#         idx = db.query(SpotTickData).filter(SpotTickData.symbol_id == stock_token).order_by(SpotTickData.id.desc()).first()
#         if not idx:
#             raise HTTPException(status_code=404, detail="Token not found")
#         return {"data": {"last_update": str(idx.timestamp), "ltp": float(idx.value)}}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.get("/indices/ltp")
def fetch_ltp(stock_token: str, db: Session = Depends(get_db)):
    try:
        print('stock_token:::', stock_token)
        symbol = db.query(SymbolMaster).filter(
            SymbolMaster.token == stock_token,
            SymbolMaster.is_active == True,
            SymbolMaster.is_deleted == False
        ).first()
        print('flag2',symbol)
        idx = (
            db.query(SpotTickData)
            .filter(SpotTickData.symbol_id == symbol.id)
            .order_by(SpotTickData.id.desc())
            .first()
        )
        print('idx:::', idx)
        if not idx:
            raise HTTPException(status_code=404, detail="Token not found")

        return {"data": {"last_update": str(idx.timestamp), "ltp": float(idx.ltp)}}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# 4. Fetch Stock Trend
@router.post("/trend")
def fetch_trend(stock_token: str = Body(...), db: Session = Depends(get_db)):
    try:
        idx = db.query(MarketIndexSchema).filter(MarketIndexSchema.name == stock_token).order_by(MarketIndexSchema.id.desc()).first()
        if not idx:
            raise HTTPException(status_code=404, detail="Token not found")
        # Example: Use is_positive to determine trend
        trend_type = "bullish" if idx.is_positive else "bearish"
        return {"data": {"trend_type": trend_type}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. Admin Kill Trade Signal
@router.post("/admin/kill-trade-signal")
def admin_kill_trade_signal(
    request: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to check if a trade should be killed for a given token.
    
    **Request Body Example:**
    ```json
    {
        "token": "99926009"
    }
    ```
    
    **Response:**
    ```json
    {
        "kill": false,
        "token": "99926009",
        "message": "No kill signal active"
    }
    ```
    
    Returns:
    - kill (boolean): true if the trade should be force-exited, false otherwise
    - token (string): The token that was checked
    - message (string): Optional message or reason
    """
    try:
        # Extract token from request body
        token = request.get("token")
        
        if not token:
            raise HTTPException(
                status_code=422,
                detail="Token is required in request body"
            )
        
        print(f"Checking kill trade signal for token: {token}")
        
        # TODO: Implement your actual kill signal logic here
        # For example, check if there's an active kill switch for this token
        from app.models.models import KillSwitch
        
        # Check if there's an active kill switch
        # kill_switch = db.query(KillSwitch).filter(
        #     KillSwitch.is_active == True,
        #     # You can add more conditions here based on your requirements
        #     # For example, filter by close_type, close_for, etc.
        # ).first()
        
        # if kill_switch:
        #     return {
        #         "kill": True,
        #         "token": token,
        #         "message": f"Kill switch active: {kill_switch.reason or 'Manual kill switch triggered'}"
        #     }
        
        # No kill signal active
        return {
            "kill": False,
            "token": token,
            "message": "No kill signal active"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in kill-trade-signal for token {token if 'token' in locals() else 'unknown'}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
