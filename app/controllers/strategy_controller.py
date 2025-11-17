"""
Strategy controller - Strategy management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.db import get_db
from app.schemas.schema import StrategySchema, StrategyCreate, StrategyUpdate, ResponseSchema
from app.services.strategy_services import StrategyService
from app.models.models import User
from app.utils.security import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.get("", response_model=ResponseSchema[List[StrategySchema]])
async def get_strategies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all strategies for current user"""
    try:
        strategies = StrategyService.get_all_strategies(db, user_id=current_user.id)
        return ResponseSchema(data=strategies, message="Strategies retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting strategies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving strategies"
        )


@router.get("/{strategy_id}", response_model=ResponseSchema[StrategySchema])
async def get_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific strategy"""
    strategy = StrategyService.get_strategy_by_id(db, strategy_id)
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    if not (strategy.user_id == current_user.id or current_user.role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this strategy"
        )
    
    return ResponseSchema(data=strategy)


@router.post("", response_model=ResponseSchema[StrategySchema], status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy_data: StrategyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new strategy"""
    try:
        new_strategy = StrategyService.create_strategy(db, strategy_data, current_user.id)
        logger.info(f"Strategy created for user {current_user.id}: {new_strategy.id}")
        return ResponseSchema(
            data=new_strategy,
            status=201,
            message="Strategy created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating strategy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating strategy"
        )


@router.put("/{strategy_id}", response_model=ResponseSchema[StrategySchema])
async def update_strategy(
    strategy_id: int,
    strategy_data: StrategyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update strategy"""
    strategy = StrategyService.get_strategy_by_id(db, strategy_id)
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    if not (strategy.user_id == current_user.id or current_user.role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this strategy"
        )
    
    try:
        updated_strategy = StrategyService.update_strategy(db, strategy_id, strategy_data)
        return ResponseSchema(data=updated_strategy, message="Strategy updated successfully")
    except Exception as e:
        logger.error(f"Error updating strategy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating strategy"
        )


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete strategy"""
    strategy = StrategyService.get_strategy_by_id(db, strategy_id)
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    if not (strategy.user_id == current_user.id or current_user.role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this strategy"
        )
    
    deleted = StrategyService.delete_strategy(db, strategy_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting strategy"
        )
    
    return None


@router.get("/active/all", response_model=ResponseSchema[List[StrategySchema]])
async def get_active_strategies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active strategies for current user"""
    try:
        strategies = StrategyService.get_active_strategies(db, current_user.id)
        return ResponseSchema(data=strategies, message="Active strategies retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting active strategies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving active strategies"
        )
