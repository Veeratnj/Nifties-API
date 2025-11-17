"""
Health controller - Health check endpoints
"""

from fastapi import APIRouter
from app.schemas.schema import ResponseSchema
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=ResponseSchema)
async def health_check():
    """Health check endpoint"""
    return ResponseSchema(
        data={"status": "ok", "version": "0.1.0"},
        message="API is running successfully"
    )


@router.get("/", response_model=ResponseSchema)
async def root():
    """Root endpoint"""
    return ResponseSchema(
        data={
            "app": "Nifties API",
            "version": "0.1.0",
            "description": "Trading Platform API for Options Trading"
        },
        message="Welcome to Nifties API"
    )
