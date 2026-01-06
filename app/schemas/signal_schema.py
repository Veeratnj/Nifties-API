"""
Signal schemas for trading entry and exit signals
"""

from pydantic import BaseModel, Field
from typing import Optional


class StrikeData(BaseModel):
    """Schema for strike data details"""
    token: str = Field(..., description="Token of the strike")
    exchange: str = Field(..., description="Exchange identifier")
    index_name: str = Field(..., description="Name of the index")
    DOE: str = Field(..., description="Date of Expiry")
    strike_price: float = Field(..., description="Strike price value")
    position: str = Field(..., description="Type of position (CE/PE)")
    symbol: str = Field(..., description="Trading symbol")
    lot_qty: int = Field(..., description="Lot quantity")


class SignalBase(BaseModel):
    """Base schema for trading signals"""
    token: str = Field(..., description="Token identifier (e.g., '23')")
    signal: str = Field(..., description="Signal type (e.g., 'BUY_ENTRY', 'SELL_ENTRY', 'BUY_EXIT', 'SELL_EXIT')")
    unique_id: str = Field(..., description="Unique ID for this signal")
    strategy_code: str = Field(..., description="Code of the strategy")
    strike_data: StrikeData = Field(..., description="Nested strike data information")


class SignalEntryRequest(SignalBase):
    """Schema for entry signal request"""
    pass


class SignalExitRequest(SignalBase):
    """Schema for exit signal request"""
    pass


class LTPInsertRequest(BaseModel):
    """Schema for manual LTP insertion"""
    token: str = Field(..., description="Token of the strike")
    ltp: float = Field(..., description="Last traded price to store")
    symbol: str = Field(..., description="Trading symbol")  


class SignalResponse(BaseModel):
    """Response schema for signal operations"""
    success: bool
    message: str
    data: Optional[dict] = None
