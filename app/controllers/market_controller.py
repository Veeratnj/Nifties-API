"""
Market controller - Market data endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.db import get_db
from app.schemas.schema import MarketIndexSchema, MarketIndexCreate, MarketIndexUpdate, PnLSchema, PnLCreate, ResponseSchema
from app.services.market_services import MarketService
from app.models.models import User
from app.utils.security import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/market", tags=["market"])


# ==================== Market Indices ====================

@router.get("/indices", response_model=ResponseSchema[List[MarketIndexSchema]])
async def get_market_indices(
    db: Session = Depends(get_db)
):
    """Get all market indices"""
    try:
        indices = MarketService.get_all_indices(db)
        return ResponseSchema(data=indices, message="Market indices retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting market indices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving market indices"
        )


@router.get("/indices/{name}", response_model=ResponseSchema[MarketIndexSchema])
async def get_index_by_name(
    name: str,
    db: Session = Depends(get_db)
):
    """Get market index by name"""
    index = MarketService.get_index_by_name(db, name)
    if not index:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Market index {name} not found"
        )
    return ResponseSchema(data=index)


@router.post("/indices", response_model=ResponseSchema[MarketIndexSchema], status_code=status.HTTP_201_CREATED)
async def create_market_index(
    index_data: MarketIndexCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new market index (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        new_index = MarketService.create_index(db, index_data)
        return ResponseSchema(
            data=new_index,
            status=201,
            message="Market index created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating market index: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating market index"
        )


@router.put("/indices/{index_id}", response_model=ResponseSchema[MarketIndexSchema])
async def update_market_index(
    index_id: int,
    index_data: MarketIndexUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update market index (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    updated_index = MarketService.update_index(db, index_id, index_data)
    if not updated_index:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market index not found"
        )
    
    return ResponseSchema(data=updated_index, message="Market index updated successfully")


@router.delete("/indices/{index_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_market_index(
    index_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete market index (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    deleted = MarketService.delete_index(db, index_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market index not found"
        )
    
    return None


# ==================== PnL ====================

@router.get("/pnl", response_model=ResponseSchema[List[PnLSchema]])
async def get_pnl_data(
    db: Session = Depends(get_db)
):
    """Get all P&L records"""
    try:
        pnl_records = MarketService.get_all_pnl(db)
        return ResponseSchema(data=pnl_records, message="PnL data retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting PnL data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving PnL data"
        )


@router.get("/pnl/{period}", response_model=ResponseSchema[PnLSchema])
async def get_pnl_by_period(
    period: str,
    db: Session = Depends(get_db)
):
    """Get P&L for specific period"""
    pnl = MarketService.get_pnl_by_period(db, period)
    if not pnl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PnL data for period {period} not found"
        )
    return ResponseSchema(data=pnl)


@router.post("/pnl", response_model=ResponseSchema[PnLSchema], status_code=status.HTTP_201_CREATED)
async def create_pnl(
    pnl_data: PnLCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create PnL record (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        new_pnl = MarketService.create_pnl(db, pnl_data)
        return ResponseSchema(
            data=new_pnl,
            status=201,
            message="PnL record created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating PnL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating PnL record"
        )



from fastapi import APIRouter, Depends
from app.services.ltp_ws_service import get_ltp, start_ltp_websocket
import asyncio

router = APIRouter()

# Example callback function to log LTP
def handle_ltp(token, ltp):
    print(f"📈 Token {token} LTP: {ltp}")

@router.post("/start-ltp/{token}")
async def start_ltp(token: str, app=Depends(lambda: app)):
    """
    Start LTP WebSocket for a token in background
    """
    # Run in a separate thread to avoid blocking FastAPI
    asyncio.create_task(
        asyncio.to_thread(
            start_ltp_websocket,
            dhan_context,  # your DhanContext object here
            token,
            app,
            handle_ltp
        )
    )
    return {"status": "LTP WebSocket started", "token": token}

@router.get("/ltp/{token}")
async def read_ltp(token: str, app=Depends(lambda: app)):
    ltp = await get_ltp(app, token)
    if ltp is None:
        return {"token": token, "ltp": None, "status": "waiting for first tick"}
    return {"token": token, "ltp": ltp}



