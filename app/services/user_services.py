"""
User service - Business logic for user operations
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models.models import User
from app.schemas.schema import UserCreate, UserUpdate, UserSchema
from app.utils.security import SecurityUtils

logger = logging.getLogger(__name__)


class UserService:
    """Service for user operations"""

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                logger.info(f"Retrieved user: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {str(e)}")
            raise

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            user = db.query(User).filter(User.email == email).first()
            if user:
                logger.info(f"Retrieved user by email: {email}")
            return user
        except Exception as e:
            logger.error(f"Error retrieving user by email: {str(e)}")
            raise

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create new user"""
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                logger.warning(f"User already exists: {user_data.email}")
                raise ValueError("User with this email already exists")
            
            # Hash password
            hashed_password = SecurityUtils.hash_password(user_data.password)
            
            new_user = User(
                email=user_data.email,
                name=user_data.name,
                password_hash=hashed_password,
                role=user_data.role
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            logger.info(f"Created new user: {new_user.email}")
            return new_user
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User not found: {user_id}")
                return None
            
            # Check if email is being updated and if it's already taken
            if user_data.email and user_data.email != user.email:
                existing_user = db.query(User).filter(User.email == user_data.email).first()
                if existing_user:
                    logger.warning(f"Email already in use: {user_data.email}")
                    raise ValueError("Email already in use")
            
            update_data = user_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(user, key, value)
            
            db.commit()
            db.refresh(user)
            logger.info(f"Updated user: {user_id}")
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User not found: {user_id}")
                return False
            
            db.delete(user)
            db.commit()
            logger.info(f"Deleted user: {user_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                logger.warning(f"Authentication failed: user not found - {email}")
                return None
            
            if not SecurityUtils.verify_password(password, user.password_hash):
                logger.warning(f"Authentication failed: invalid password - {email}")
                return None
            
            if not user.is_active:
                logger.warning(f"Authentication failed: inactive user - {email}")
                return None
            
            logger.info(f"User authenticated: {email}")
            return user
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            raise

    @staticmethod
    def activate_user(db: Session, user_id: int) -> Optional[User]:
        """Activate user"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            user.is_active = True
            db.commit()
            db.refresh(user)
            logger.info(f"Activated user: {user_id}")
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"Error activating user {user_id}: {str(e)}")
            raise

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> Optional[User]:
        """Deactivate user"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            user.is_active = False
            db.commit()
            db.refresh(user)
            logger.info(f"Deactivated user: {user_id}")
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"Error deactivating user {user_id}: {str(e)}")
            raise
