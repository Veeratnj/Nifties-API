"""
Log service - Business logic for system logs
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import logging

from app.models.models import SystemLog
from app.schemas.schema import LogCreate

logger = logging.getLogger(__name__)


class LogService:
    """Service class for log operations"""
    
    @staticmethod
    def get_all_logs(
        db: Session,
        user_id: Optional[int] = None,
        level: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[SystemLog]:
        """
        Get all logs with optional filtering
        
        Args:
            db: Database session
            user_id: Filter by user ID (None for all users, admin only)
            level: Filter by log level (DEBUG, INFO, WARNING, ERROR)
            category: Filter by category
            limit: Maximum number of records to return (max 500)
        
        Returns:
            List of SystemLog objects
        """
        try:
            query = db.query(SystemLog)
            
            # Apply filters
            if user_id is not None:
                query = query.filter(SystemLog.user_id == user_id)
            
            if level:
                query = query.filter(SystemLog.level == level)
            
            if category:
                query = query.filter(SystemLog.category == category)
            
            # Apply limit (max 500)
            limit = min(limit, 500)
            
            # Order by timestamp descending (newest first)
            logs = query.order_by(desc(SystemLog.timestamp)).limit(limit).all()
            
            logger.info(f"Retrieved {len(logs)} log entries")
            return logs
            
        except Exception as e:
            logger.error(f"Error retrieving logs: {str(e)}")
            raise
    
    @staticmethod
    def get_log_by_id(db: Session, log_id: int) -> Optional[SystemLog]:
        """
        Get specific log by ID
        
        Args:
            db: Database session
            log_id: Log ID
        
        Returns:
            SystemLog object or None
        """
        try:
            log = db.query(SystemLog).filter(SystemLog.id == log_id).first()
            return log
        except Exception as e:
            logger.error(f"Error retrieving log {log_id}: {str(e)}")
            raise
    
    @staticmethod
    def create_log(
        db: Session,
        log_data: LogCreate,
        user_id: Optional[int] = None
    ) -> SystemLog:
        """
        Create new log entry
        
        Args:
            db: Database session
            log_data: Log creation data
            user_id: Associated user ID
        
        Returns:
            Created SystemLog object
        """
        try:
            # Create log entry
            new_log = SystemLog(
                level=log_data.level,
                message=log_data.message,
                category=log_data.category,
                source=log_data.source,
                user_id=user_id or log_data.user_id,
                log_metadata=log_data.metadata
            )
            
            db.add(new_log)
            db.commit()
            db.refresh(new_log)
            
            logger.info(f"Created log entry: {new_log.id}")
            return new_log
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating log: {str(e)}")
            raise
