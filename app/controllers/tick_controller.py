"""
Controller for Tick Data Insert API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Optional
from pydantic import BaseModel

from app.db.db import get_db
# from app.schemas.tick_schema import  StrikePriceLTPInsert, OHLCDataInsert
from app.schemas.schema import TickDataInsert,StrikePriceLTPInsert,OHLCDataInsert
from app.schemas.schema import ApiResponse
from app.services.tick_service import TickLTPService

router = APIRouter(
    prefix="/api/tick",
    tags=["Tick Data"]
)


@router.post("/insert-spot-ltp", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def insert_spot_ltp(
    tick_data: TickDataInsert,
    db: Session = Depends(get_db)
):
    """
    Insert tick data (LTP) for a symbol using token
    
    **Request Body Example:**
    ```json
    {
        "token": "25",
        "timestamp": "2025-11-25T14:30:45",
        "ltp": 18500.50,
        
    }
    ```
    
    **Response:**
    - 201: Tick data inserted successfully
    - 400: Invalid data (e.g., token not found)
    - 500: Server error
    """
    try:
        print('check123',tick_data)
        # Delegate to service layer
        db_tick = TickLTPService.insert_spot_ltp(db, tick_data)
        
        return ApiResponse(
            success=True,
            message="Spot LTP data inserted successfully",
            data=TickLTPService.format_spot_ltp_response(db_tick)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



@router.post("/insert-strike-ltp", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def insert_strike_price_ltp(
    strike_ltp_data: StrikePriceLTPInsert,
    db: Session = Depends(get_db)
):
    """
    Insert strike price LTP data
    
    **Request Body Example:**
    ```json
    {
        "strike_price_token": 'token',
        "ltp": 125.50,
        "timestamp": "2025-11-25T14:30:45"
    }
    ```
    
    **Response:**
    - 201: Strike price LTP data inserted successfully
    - 400: Invalid data
    - 500: Server error
    """
    try:
        # Delegate to service layer
        db_strike_ltp = TickLTPService.insert_strike_ltp(db, strike_ltp_data)
        
        return ApiResponse(
            success=True,
            message="Strike price LTP data inserted successfully",
            data=TickLTPService.format_strike_ltp_response(db_strike_ltp)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/insert-ohlc", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def insert_ohlc_data(
    ohlc_data: OHLCDataInsert,
    db: Session = Depends(get_db)
):
    """
    Insert OHLC (Open, High, Low, Close) historical data
    
    **Request Body Example:**
    ```json
    {
        "symbol": "NIFTY",
        "timeframe": "5_MIN",
        "timestamp": "2025-11-25T13:00:00",
        "open": 18500.00,
        "high": 18525.50,
        "low": 18495.25,
        "close": 18510.75,
        "volume": 1500000
    }
    ```
    
    **Valid Timeframes:**
    - 5_SEC, 10_SEC, 15_SEC, 30_SEC
    - 1_MIN, 5_MIN, 15_MIN, 30_MIN, 60_MIN
    - 1_DAY
    
    **Response:**
    - 201: OHLC data inserted successfully
    - 400: Invalid data or timeframe
    - 500: Server error
    """
    try:
        # Delegate to service layer
        db_ohlc = TickLTPService.insert_ohlc_data(db, ohlc_data)
        
        return ApiResponse(
            success=True,
            message="OHLC data inserted successfully",
            data=TickLTPService.format_ohlc_response(db_ohlc)
        )
    
    except Exception as e:
        print(f"DEBUG: Exception in insert_ohlc_data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


