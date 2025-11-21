
from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.services.market_services import MarketService
from app.schemas.schema import MarketIndexSchema, PnLSchema

router = APIRouter(prefix="/db", tags=["nifties-opt"])

# 1. Get Nifty Tokens
@router.get("/nifty-tokens")
def get_nifty_tokens(db: Session = Depends(get_db)):
    # Example: Return all unique index names from MarketIndex
    try:
        indices = MarketService.get_all_indices(db)
        tokens = [idx.name for idx in indices]
        return {"tokens": tokens}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Fetch OHLC Data
@router.post("/ohlc")
def fetch_ohlc(token: str = Body(...), limit: int = Body(500), db: Session = Depends(get_db)):
    # Example: Return last N records for the given token from MarketIndex (simulate OHLC)
    try:
        # This is a placeholder. Replace with your actual OHLC logic if you have OHLC table.
        indices = db.query(MarketIndexSchema).filter(MarketIndexSchema.name == token).order_by(MarketIndexSchema.id.desc()).limit(limit).all()
        data = [
            {
                "start_time": str(idx.timestamp),
                "open": float(idx.value),
                "high": float(idx.value),
                "low": float(idx.value),
                "close": float(idx.value)
            } for idx in indices
        ]
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Fetch Latest LTP
@router.post("/ltp")
def fetch_ltp(stock_token: str = Body(...), db: Session = Depends(get_db)):
    try:
        idx = db.query(MarketIndexSchema).filter(MarketIndexSchema.name == stock_token).order_by(MarketIndexSchema.id.desc()).first()
        if not idx:
            raise HTTPException(status_code=404, detail="Token not found")
        return {"data": {"last_update": str(idx.timestamp), "ltp": float(idx.value)}}
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
def admin_kill_trade_signal(token: str = Body(...)):
    # This is a placeholder. Implement your own logic for admin-triggered exit.
    # For now, always return kill: false
    return {"kill": False}
