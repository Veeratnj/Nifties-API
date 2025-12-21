"""
Trade controller - Trade management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.db import get_db
from app.schemas.schema import TradeSchema, TradeCreate, TradeUpdate, ResponseSchema, PositionSchema
from app.services.trade_services import TradeService
from app.services.position_service import PositionService
from app.models.models import User
from app.utils.security import get_current_user, check_user_owns_resource
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trades", tags=["trades"])


@router.get("", response_model=ResponseSchema)
async def get_trades(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get live positions (active trades) based on user role:
    - SUPERADMIN/ADMIN: See ALL users' trades
    - USER/TRADER: See only their own trades
    """
    try:
        # Pass user role for access control
        print("hihi")
        positions = PositionService.get_all_positions(
            db, 
            user_id=current_user.id,
            user_role=current_user.role.value  # Pass the role enum value
        )
        return ResponseSchema(data=positions, message="Trades retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting trades: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving trades"
        )


@router.get("/{trade_id}", response_model=ResponseSchema[TradeSchema])
async def get_trade(
    trade_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific trade"""
    trade = TradeService.get_trade_by_id(db, trade_id)
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )
    
    if not (trade.user_id == current_user.id or current_user.role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this trade"
        )
    
    return ResponseSchema(data=trade)


@router.post("", response_model=ResponseSchema[TradeSchema], status_code=status.HTTP_201_CREATED)
async def create_trade(
    trade_data: TradeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new trade"""
    # Check if user is authorized to create Master Trades (e.g. ADMIN/SUPERADMIN)
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create Master Trades"
        )

    try:
        # Service now handles multi-user execution, no user_id passed
        new_trade = TradeService.create_trade(db, trade_data)
        logger.info(f"Master Trade created by {current_user.id}: {new_trade.id}")
        return ResponseSchema(
            data=new_trade,
            status=201,
            message="Trade created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating trade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating trade"
        )


@router.put("/{trade_id}", response_model=ResponseSchema[TradeSchema])
async def update_trade(
    trade_id: int,
    trade_data: TradeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update trade"""
    trade = TradeService.get_trade_by_id(db, trade_id)
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )
    
    # Only Admin can update Master Trade
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this trade"
        )
    
    try:
        updated_trade = TradeService.update_trade(db, trade_id, trade_data)
        return ResponseSchema(data=updated_trade, message="Trade updated successfully")
    except Exception as e:
        logger.error(f"Error updating trade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating trade"
        )


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trade(
    trade_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete trade"""
    trade = TradeService.get_trade_by_id(db, trade_id)
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )
    
    # Only Admin can delete Master Trade
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this trade"
        )
    
    deleted = TradeService.delete_trade(db, trade_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting trade"
        )
    
    return None


@router.get("/active/all", response_model=ResponseSchema[List[TradeSchema]])
async def get_active_trades(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active trades for current user"""
    try:
        trades = TradeService.get_active_trades(db, current_user.id)
        return ResponseSchema(data=trades, message="Active trades retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting active trades: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving active trades"
        )


@router.post("/{trade_id}/close", response_model=ResponseSchema[TradeSchema])
async def close_trade(
    trade_id: int,
    closing_price: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Close trade with final price"""
    trade = TradeService.get_trade_by_id(db, trade_id)
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )
    
    # Only Admin can close Master Trade (which triggers exits for all)
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to close this trade"
        )
    
    try:
        closed_trade = TradeService.close_trade(db, trade_id, closing_price)
        return ResponseSchema(data=closed_trade, message="Trade closed successfully")
    except Exception as e:
        logger.error(f"Error closing trade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error closing trade"
        )
