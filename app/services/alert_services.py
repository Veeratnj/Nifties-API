"""
Alert service - Business logic for user alerts/notifications
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import logging

from app.models.models import Notification
from app.schemas.schema import AlertCreate

logger = logging.getLogger(__name__)


class AlertService:
    """Service class for alert operations"""
    
    @staticmethod
    def get_all_alerts(
        db: Session,
        user_id: int,
        is_read: Optional[bool] = None
    ) -> List[Notification]:
        """
        Get all alerts for a user
        
        Args:
            db: Database session
            user_id: User ID
            is_read: Filter by read status (None for all)
        
        Returns:
            List of Notification objects
        """
        try:
            query = db.query(Notification).filter(Notification.user_id == user_id)
            
            if is_read is not None:
                query = query.filter(Notification.is_read == is_read)
            
            # Order by created_at descending (newest first)
            alerts = query.order_by(desc(Notification.created_at)).all()
            
            logger.info(f"Retrieved {len(alerts)} alerts for user {user_id}")
            return alerts
            
        except Exception as e:
            logger.error(f"Error retrieving alerts: {str(e)}")
            raise
    
    @staticmethod
    def get_alert_by_id(db: Session, alert_id: int) -> Optional[Notification]:
        """
        Get specific alert by ID
        
        Args:
            db: Database session
            alert_id: Alert ID
        
        Returns:
            Notification object or None
        """
        try:
            alert = db.query(Notification).filter(Notification.id == alert_id).first()
            return alert
        except Exception as e:
            logger.error(f"Error retrieving alert {alert_id}: {str(e)}")
            raise
    
    @staticmethod
    def create_alert(
        db: Session,
        alert_data: AlertCreate,
        user_id: int
    ) -> Notification:
        """
        Create new alert for user
        
        Args:
            db: Database session
            alert_data: Alert creation data
            user_id: User ID
        
        Returns:
            Created Notification object
        """
        try:
            # Create notification
            new_alert = Notification(
                user_id=user_id,
                title=alert_data.message,  # Use message as title
                message=alert_data.message,
                notification_type=alert_data.alert_type,
                is_read=False
            )
            
            db.add(new_alert)
            db.commit()
            db.refresh(new_alert)
            
            logger.info(f"Created alert for user {user_id}: {new_alert.id}")
            return new_alert
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating alert: {str(e)}")
            raise
    
    @staticmethod
    def mark_as_read(db: Session, alert_id: int) -> Optional[Notification]:
        """
        Mark alert as read
        
        Args:
            db: Database session
            alert_id: Alert ID
        
        Returns:
            Updated Notification object or None
        """
        try:
            alert = db.query(Notification).filter(Notification.id == alert_id).first()
            
            if not alert:
                return None
            
            alert.is_read = True
            alert.read_at = datetime.utcnow()
            
            db.commit()
            db.refresh(alert)
            
            logger.info(f"Marked alert {alert_id} as read")
            return alert
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error marking alert as read: {str(e)}")
            raise
    
    @staticmethod
    def delete_alert(db: Session, alert_id: int) -> bool:
        """
        Delete alert
        
        Args:
            db: Database session
            alert_id: Alert ID
        
        Returns:
            True if deleted, False if not found
        """
        try:
            alert = db.query(Notification).filter(Notification.id == alert_id).first()
            
            if not alert:
                return False
            
            db.delete(alert)
            db.commit()
            
            logger.info(f"Deleted alert {alert_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting alert: {str(e)}")
            raise
