"""
Alert controller - User alerts/notifications endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.db import get_db
from app.schemas.schema import AlertSchema, AlertCreate, ResponseSchema
from app.services.alert_services import AlertService
from app.models.models import User
from app.utils.security import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=ResponseSchema[List[AlertSchema]])
async def get_alerts(
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all alerts for current user"""
    try:
        alerts = AlertService.get_all_alerts(
            db=db,
            user_id=current_user.id,
            is_read=is_read
        )
        
        return ResponseSchema(
            data=alerts,
            message=f"Retrieved {len(alerts)} alerts"
        )
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving alerts"
        )


@router.get("/{alert_id}", response_model=ResponseSchema[AlertSchema])
async def get_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific alert by ID"""
    alert = AlertService.get_alert_by_id(db, alert_id)
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Check authorization (users can only see their own alerts, admins see all)
    if alert.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this alert"
        )
    
    return ResponseSchema(data=alert)


@router.post("", response_model=ResponseSchema[AlertSchema], status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new alert for current user"""
    try:
        new_alert = AlertService.create_alert(db, alert_data, current_user.id)
        logger.info(f"Alert created for user {current_user.id}: {new_alert.id}")
        
        return ResponseSchema(
            data=new_alert,
            status=201,
            message="Alert created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating alert: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating alert"
        )


@router.patch("/{alert_id}/read", response_model=ResponseSchema[AlertSchema])
async def mark_alert_as_read(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark alert as read"""
    # Get alert and check authorization
    alert = AlertService.get_alert_by_id(db, alert_id)
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    if alert.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this alert"
        )
    
    try:
        updated_alert = AlertService.mark_as_read(db, alert_id)
        return ResponseSchema(
            data=updated_alert,
            message="Alert marked as read"
        )
    except Exception as e:
        logger.error(f"Error marking alert as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating alert"
        )


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete alert"""
    # Get alert and check authorization
    alert = AlertService.get_alert_by_id(db, alert_id)
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    if alert.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this alert"
        )
    
    deleted = AlertService.delete_alert(db, alert_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting alert"
        )
    
    return None
