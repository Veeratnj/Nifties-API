"""
Signal schemas for trading entry and exit signals
"""

from pydantic import BaseModel, Field
from typing import Optional


class SignalBase(BaseModel):
    """Base schema for trading signals"""
    token: str = Field(..., description="Token identifier (e.g., '23')")
    signal: str = Field(..., description="Signal type (e.g., 'BUY_ENTRY', 'SELL_ENTRY', 'BUY_EXIT', 'SELL_EXIT')")
    unique_id: str = Field(..., description="Unique ID for this signal")
    strike_price_token: str = Field(..., description="Strike price token")
    strategy_code: str = Field(..., description="Code of the strategy")


class SignalEntryRequest(SignalBase):
    """Schema for entry signal request"""
    pass


class SignalExitRequest(SignalBase):
    """Schema for exit signal request"""
    pass


class SignalResponse(BaseModel):
    """Response schema for signal operations"""
    success: bool
    message: str
    data: Optional[dict] = None
