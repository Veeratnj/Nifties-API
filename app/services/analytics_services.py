"""
Analytics service - Business logic for analytics operations
"""

import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.models import Analytics
from app.schemas.schema import AnalyticsSchema, AnalyticsCreate

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics operations"""

    @staticmethod
    def get_all_analytics(db: Session) -> List[Analytics]:
        """Get all analytics records"""
        try:
            analytics = db.query(Analytics).order_by(Analytics.date.desc()).all()
            logger.info(f"Retrieved {len(analytics)} analytics records")
            return analytics
        except Exception as e:
            logger.error(f"Error retrieving analytics: {str(e)}")
            raise

    @staticmethod
    def get_analytics_by_date(db: Session, date: str) -> Optional[Analytics]:
        """Get analytics for specific date (YYYY-MM-DD)"""
        try:
            analytics = db.query(Analytics).filter(Analytics.date == date).first()
            if analytics:
                logger.info(f"Retrieved analytics for date: {date}")
            return analytics
        except Exception as e:
            logger.error(f"Error retrieving analytics for {date}: {str(e)}")
            raise

    @staticmethod
    def create_analytics(db: Session, analytics_data: AnalyticsCreate) -> Analytics:
        """Create analytics record"""
        try:
            # Check if record already exists for this date
            existing = db.query(Analytics).filter(Analytics.date == analytics_data.date).first()
            if existing:
                logger.warning(f"Analytics already exists for date: {analytics_data.date}")
                raise ValueError("Analytics already exists for this date")
            
            # Calculate additional metrics
            analytics_dict = analytics_data.dict()
            
            if analytics_dict["total_trades"] > 0:
                analytics_dict["win_rate"] = (analytics_dict["winning_trades"] / analytics_dict["total_trades"]) * 100
                analytics_dict["average_win"] = analytics_dict["total_pnl"] / analytics_dict["winning_trades"] if analytics_dict["winning_trades"] > 0 else 0
                analytics_dict["average_loss"] = abs(analytics_dict["total_pnl"]) / analytics_dict["losing_trades"] if analytics_dict["losing_trades"] > 0 else 0
                analytics_dict["profit_factor"] = abs(analytics_dict["average_win"] / analytics_dict["average_loss"]) if analytics_dict["average_loss"] > 0 else 0
            
            new_analytics = Analytics(**analytics_dict)
            db.add(new_analytics)
            db.commit()
            db.refresh(new_analytics)
            logger.info(f"Created analytics record for date: {new_analytics.date}")
            return new_analytics
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating analytics: {str(e)}")
            raise

    @staticmethod
    def update_analytics(db: Session, analytics_id: int, analytics_data: AnalyticsCreate) -> Optional[Analytics]:
        """Update analytics record"""
        try:
            analytics = db.query(Analytics).filter(Analytics.id == analytics_id).first()
            if not analytics:
                logger.warning(f"Analytics not found: {analytics_id}")
                return None
            
            # Recalculate metrics
            analytics.total_trades = analytics_data.total_trades
            analytics.winning_trades = analytics_data.winning_trades
            analytics.losing_trades = analytics_data.losing_trades
            analytics.total_pnl = analytics_data.total_pnl
            
            if analytics_data.total_trades > 0:
                analytics.win_rate = (analytics_data.winning_trades / analytics_data.total_trades) * 100
                analytics.average_win = analytics_data.total_pnl / analytics_data.winning_trades if analytics_data.winning_trades > 0 else 0
                analytics.average_loss = abs(analytics_data.total_pnl) / analytics_data.losing_trades if analytics_data.losing_trades > 0 else 0
                analytics.profit_factor = abs(analytics.average_win / analytics.average_loss) if analytics.average_loss > 0 else 0
            
            db.commit()
            db.refresh(analytics)
            logger.info(f"Updated analytics: {analytics_id}")
            return analytics
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating analytics {analytics_id}: {str(e)}")
            raise

    @staticmethod
    def get_analytics_range(db: Session, start_date: str, end_date: str) -> List[Analytics]:
        """Get analytics for date range"""
        try:
            analytics = db.query(Analytics).filter(
                Analytics.date >= start_date,
                Analytics.date <= end_date
            ).order_by(Analytics.date.desc()).all()
            logger.info(f"Retrieved {len(analytics)} analytics records for range {start_date} to {end_date}")
            return analytics
        except Exception as e:
            logger.error(f"Error retrieving analytics range: {str(e)}")
            raise

    @staticmethod
    def get_latest_analytics(db: Session, days: int = 30) -> List[Analytics]:
        """Get latest analytics records"""
        try:
            analytics = db.query(Analytics).order_by(Analytics.date.desc()).limit(days).all()
            logger.info(f"Retrieved latest {len(analytics)} analytics records")
            return analytics
        except Exception as e:
            logger.error(f"Error retrieving latest analytics: {str(e)}")
            raise
