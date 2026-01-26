"""
Market controller - Market data endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.signal_schema import AdminSignalEntryRequest, AdminSignalExitRequest

from app.db.db import get_db
from app.models.models import User
from app.utils.security import get_current_user
from app.services.admin_services import AdminService
from app.schemas.schema import SignalResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/create-live-trade-for-all-users/v1",response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def create_live_trade_for_all_users_v1(
    signal_data: AdminSignalEntryRequest,
    request: Request,
    db: Session = Depends(get_db)):
    '''
    Create live trade for all users
    payload is AdminSignalEntryRequest
    {
  "token": "23",
  "signal": "BUY_ENTRY",
  "unique_id": "ADMIN-BUY-0001",
  "strategy_code": "BNF_BREAKOUT",
  "user_ids": [101, 102, 103],
  "strike_data": {
    "token": "56789",
    "exchange": "NFO",
    "index_name": "BANKNIFTY",
    "DOE": "2026-01-30",
    "strike_price": 46500,
    "position": "CE",
    "symbol": "BANKNIFTY30JAN26CE46500",
    "lot_qty": 15
  }
}

    '''
    try:
        AdminService.create_live_trade_for_all_users_v1(db=db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/create-live-trade-for-user/v1",response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def create_live_trade_for_user_v1(
    signal_data: AdminSignalEntryRequest,
    request: Request,
    db: Session = Depends(get_db)):
    '''
    Create live trade for user
    payload is AdminSignalEntryRequest
    {
  "token": "23",
  "signal": "BUY_EXIT",
  "unique_id": "ADMIN-BUY-0001",
  "strategy_code": "BNF_BREAKOUT",
  "user_ids": [101, 102, 103],
  "strike_data": {
    "token": "56789",
    "exchange": "NFO",
    "index_name": "BANKNIFTY",
    "DOE": "2026-01-30",
    "strike_price": 46500,
    "position": "CE",
    "symbol": "BANKNIFTY30JAN26CE46500",
    "lot_qty": 15
  }
}

    '''
    try:
        AdminService.create_live_trade_for_user_v1(db=db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/close-live-trade-for-all-users/v1",response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def close_live_trade_for_all_users_v1(
    signal_data: AdminSignalExitRequest,
    db: Session = Depends(get_db)):
    '''
    Close live trade for all users
    payload is AdminSignalExitRequest
    {
  "token": "23",
  "signal": "BUY_EXIT",
  "unique_id": "ADMIN-BUY-0001",
  "strategy_code": "BNF_BREAKOUT",
  "user_ids": [101, 102, 103],
  "strike_data": {
    "token": "56789",
    "exchange": "NFO",
    "index_name": "BANKNIFTY",
    "DOE": "2026-01-30",
    "strike_price": 46500,
    "position": "CE",
    "symbol": "BANKNIFTY30JAN26CE46500",
    "lot_qty": 15
  }
}

    '''
    try:
        AdminService.close_live_trade_for_all_users_v1(db=db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/close-live-trade-for-user/v1",response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def close_live_trade_for_user_v1(
    signal_data: AdminSignalExitRequest,
    db: Session = Depends(get_db)):
    '''
    {
  "token": "23",
  "signal": "BUY_EXIT",
  "unique_id": "ADMIN-BUY-0001",
  "strategy_code": "BNF_BREAKOUT",
  "user_ids": [101, 102, 103],
  "strike_data": {
    "token": "56789",
    "exchange": "NFO",
    "index_name": "BANKNIFTY",
    "DOE": "2026-01-30",
    "strike_price": 46500,
    "position": "CE",
    "symbol": "BANKNIFTY30JAN26CE46500",
    "lot_qty": 15
  }
}

    '''
    try:
        AdminService.close_live_trade_for_user_v1(db=db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
