"""
Log controller - System log endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.db import get_db
from app.schemas.schema import LogSchema, LogCreate, ResponseSchema
from app.services.log_services import LogService
from app.models.models import User
from app.utils.security import get_current_user, get_current_admin
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("", response_model=ResponseSchema[List[LogSchema]])
async def get_logs(
    level: Optional[str] = Query(None, description="Filter by log level (DEBUG, INFO, WARNING, ERROR)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, ge=1, le=500, description="Number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get system logs
    - Admin users see all logs
    - Regular users see only their own logs
    """
    try:
        # Admins can see all logs, users see only their own
        user_id = None if current_user.role == "admin" else current_user.id
        
        logs = LogService.get_all_logs(
            db=db,
            user_id=user_id,
            level=level,
            category=category,
            limit=limit
        )
        
        return ResponseSchema(
            data=logs,
            message=f"Retrieved {len(logs)} log entries"
        )
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving logs"
        )


@router.get("/{log_id}", response_model=ResponseSchema[LogSchema])
async def get_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific log entry by ID"""
    log = LogService.get_log_by_id(db, log_id)
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log entry not found"
        )
    
    # Check authorization (admin can see all, users only their own)
    if current_user.role != "admin" and log.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this log entry"
        )
    
    return ResponseSchema(data=log)


@router.post("", response_model=ResponseSchema[LogSchema], status_code=status.HTTP_201_CREATED)
async def create_log(
    log_data: LogCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create new log entry (Admin only)
    This endpoint is for manual log creation or external system integration
    """
    try:
        new_log = LogService.create_log(db, log_data)
        logger.info(f"Log entry created by admin {current_user.id}: {new_log.id}")
        
        return ResponseSchema(
            data=new_log,
            status=201,
            message="Log entry created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating log: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating log entry"
        )
