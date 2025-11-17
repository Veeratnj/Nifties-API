"""
User controller - User management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.db import get_db
from app.schemas.schema import UserSchema, UserUpdate, ResponseSchema
from app.services.user_services import UserService
from app.models.models import User
from app.utils.security import get_current_user, get_current_admin
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=ResponseSchema[UserSchema])
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return ResponseSchema(data=UserSchema.from_orm(current_user))


@router.put("/me", response_model=ResponseSchema[UserSchema])
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    try:
        updated_user = UserService.update_user(db, current_user.id, user_data)
        return ResponseSchema(
            data=UserSchema.from_orm(updated_user),
            message="User profile updated successfully"
        )
    except ValueError as e:
        logger.warning(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user"
        )


@router.get("", response_model=ResponseSchema[List[UserSchema]])
async def get_all_users(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users (Admin only)"""
    try:
        users = db.query(User).all()
        return ResponseSchema(
            data=[UserSchema.from_orm(u) for u in users],
            message="Users retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )


@router.get("/{user_id}", response_model=ResponseSchema[UserSchema])
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific user"""
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user"
        )
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return ResponseSchema(data=UserSchema.from_orm(user))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete user (Admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    deleted = UserService.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return None


@router.post("/{user_id}/activate", response_model=ResponseSchema[UserSchema])
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Activate user (Admin only)"""
    try:
        user = UserService.activate_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return ResponseSchema(
            data=UserSchema.from_orm(user),
            message="User activated successfully"
        )
    except Exception as e:
        logger.error(f"Error activating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error activating user"
        )


@router.post("/{user_id}/deactivate", response_model=ResponseSchema[UserSchema])
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Deactivate user (Admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    try:
        user = UserService.deactivate_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return ResponseSchema(
            data=UserSchema.from_orm(user),
            message="User deactivated successfully"
        )
    except Exception as e:
        logger.error(f"Error deactivating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deactivating user"
        )
