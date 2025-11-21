"""
Authentication controller - Login and registration endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.schemas.schema import LoginSchema, TokenSchema, UserCreate, UserSchema, LoginResponseSchema
from app.services.user_services import UserService
from app.utils.security import SecurityUtils, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from app.models.models import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponseSchema)
async def login(
    credentials: LoginSchema,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token"""
    user = UserService.authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        logger.warning(f"Failed login attempt for {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = SecurityUtils.create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserSchema.from_orm(user)
    }


@router.post("/register", response_model=UserSchema)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register new user"""
    try:
        user = UserService.create_user(db, user_data)
        return UserSchema.from_orm(user)
    except ValueError as e:
        logger.warning(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """Refresh JWT token"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = SecurityUtils.create_access_token(
        data={"sub": current_user.id, "email": current_user.email, "role": current_user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
