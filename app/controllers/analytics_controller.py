"""
Analytics controller - Analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.db import get_db
from app.schemas.schema import AnalyticsSchema, AnalyticsCreate, ResponseSchema
from app.services.analytics_services import AnalyticsService
from app.models.models import User
from app.utils.security import get_current_user, get_current_admin
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("", response_model=ResponseSchema[List[AnalyticsSchema]])
async def get_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all analytics records"""
    try:
        analytics = AnalyticsService.get_all_analytics(db)
        return ResponseSchema(data=analytics, message="Analytics retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving analytics"
        )


@router.get("/date/{date}", response_model=ResponseSchema[AnalyticsSchema])
async def get_analytics_by_date(
    date: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for specific date (YYYY-MM-DD format)"""
    try:
        analytics = AnalyticsService.get_analytics_by_date(db, date)
        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analytics for date {date} not found"
            )
        return ResponseSchema(data=analytics)
    except Exception as e:
        logger.error(f"Error getting analytics for date {date}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving analytics"
        )


@router.post("", response_model=ResponseSchema[AnalyticsSchema], status_code=status.HTTP_201_CREATED)
async def create_analytics(
    analytics_data: AnalyticsCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create analytics record (Admin only)"""
    try:
        new_analytics = AnalyticsService.create_analytics(db, analytics_data)
        logger.info(f"Analytics record created for date: {new_analytics.date}")
        return ResponseSchema(
            data=new_analytics,
            status=201,
            message="Analytics record created successfully"
        )
    except ValueError as e:
        logger.warning(f"Error creating analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating analytics"
        )


@router.get("/range", response_model=ResponseSchema[List[AnalyticsSchema]])
async def get_analytics_range(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for date range"""
    try:
        analytics = AnalyticsService.get_analytics_range(db, start_date, end_date)
        return ResponseSchema(
            data=analytics,
            message=f"Analytics retrieved for range {start_date} to {end_date}"
        )
    except Exception as e:
        logger.error(f"Error getting analytics range: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving analytics"
        )


@router.get("/latest", response_model=ResponseSchema[List[AnalyticsSchema]])
async def get_latest_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get latest analytics records"""
    try:
        analytics = AnalyticsService.get_latest_analytics(db, days)
        return ResponseSchema(
            data=analytics,
            message=f"Latest {len(analytics)} analytics records retrieved"
        )
    except Exception as e:
        logger.error(f"Error getting latest analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving analytics"
        )
