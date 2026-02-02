"""
Market controller - Market data endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.signal_schema import AdminSignalEntryRequest, AdminSignalExitRequest ,InstrumentEditRequest

from app.db.db import get_db
from app.models.models import User
from app.utils.security import get_current_user
from app.services.admin_services import AdminService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/create-live-trade-for-all-users/v1", status_code=status.HTTP_201_CREATED)
async def create_live_trade_for_all_users_v1(
    signal_data: AdminSignalEntryRequest,
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


@router.post("/create-live-trade-for-user/v1", status_code=status.HTTP_201_CREATED)
async def create_live_trade_for_user_v1(
    signal_data: AdminSignalEntryRequest,
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


@router.post("/close-live-trade-for-all-users/v1", status_code=status.HTTP_201_CREATED)
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


@router.post("/close-live-trade-for-user/v1", status_code=status.HTTP_201_CREATED)
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



@router.get("/show-all-live-trades/v1", status_code=status.HTTP_200_OK)
async def show_all_live_trades_v1(db: Session = Depends(get_db)):
  try:
    return AdminService.show_all_today_live_trades_v1(db=db)
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.put("/kill-trade/v1", status_code=status.HTTP_201_CREATED)
async def kill_trade_v1(unique_id:str,db: Session = Depends(get_db)):
  try:
    return AdminService.kill_trade_v1(unique_id=unique_id,db=db)
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))




@router.put("/update-stop-loss-target/v1", status_code=status.HTTP_201_CREATED)
async def update_stop_loss_target_v1(unique_id:str,stop_loss:float,target:float,db: Session = Depends(get_db)):
  try:
    return AdminService.update_stop_loss_target_v1(unique_id=unique_id,stop_loss=stop_loss,target=target,db=db)
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.get("/get-all-instruments/v1", status_code=status.HTTP_200_OK)
async def get_all_instruments_v1(db: Session = Depends(get_db)):
  try:
    return AdminService.get_all_instruments_v1(db=db)
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/edit-instrument/v1", status_code=status.HTTP_201_CREATED)
async def edit_instrument_v1(instrument_info:InstrumentEditRequest,db: Session = Depends(get_db)):
  try:
    return AdminService.edit_instrument_v1(instrument_info=instrument_info,db=db)
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


