"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Any, Generic, TypeVar
from datetime import datetime
from enum import Enum


# ==================== Enums ====================

class TradeStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    PENDING = "PENDING"


class OrderStatusEnum(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class StrategyStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    COMPLETED = "COMPLETED"


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    TRADER = "trader"
    USER = "user"


class AlertTypeEnum(str, Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"


class LogLevelEnum(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


# ==================== User Schemas ====================

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    role: UserRoleEnum = UserRoleEnum.USER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[UserRoleEnum] = None
    is_active: Optional[bool] = None


class UserSchema(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Market Index Schemas ====================

class MarketIndexSchema(BaseModel):
    id: Optional[int] = None
    name: str
    value: float
    change: float
    change_percent: float
    is_positive: bool = True
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class MarketIndexCreate(BaseModel):
    name: str
    value: float
    change: float
    change_percent: float
    is_positive: bool = True


class MarketIndexUpdate(BaseModel):
    value: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    is_positive: Optional[bool] = None


# ==================== PnL Schemas ====================

class PnLSchema(BaseModel):
    id: Optional[int] = None
    period: str  # today, week, month
    value: float
    is_positive: bool = True
    description: Optional[str] = None
    trades: int = 0
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class PnLCreate(BaseModel):
    period: str
    value: float
    is_positive: bool = True
    description: Optional[str] = None
    trades: int = 0


class PnLUpdate(BaseModel):
    value: Optional[float] = None
    is_positive: Optional[bool] = None
    description: Optional[str] = None
    trades: Optional[int] = None


# ==================== Trade Schemas ====================

class TradeBase(BaseModel):
    symbol: str
    index: str
    strike: int
    type: str  # CE or PE
    qty: int = Field(..., gt=0)
    entry_price: float = Field(..., gt=0)
    current_price: float = Field(..., gt=0)
    status: TradeStatusEnum = TradeStatusEnum.ACTIVE
    strategy: Optional[str] = None


class TradeCreate(TradeBase):
    pass


class TradeUpdate(BaseModel):
    current_price: Optional[float] = Field(None, gt=0)
    status: Optional[TradeStatusEnum] = None
    strategy: Optional[str] = None


class TradeSchema(TradeBase):
    id: int
    user_id: int
    pnl: float
    pnl_percent: float
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Order Schemas ====================

class OrderBase(BaseModel):
    symbol: str
    order_type: str  # BUY or SELL
    qty: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    status: OrderStatusEnum = OrderStatusEnum.PENDING


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = None
    executed_price: Optional[float] = Field(None, gt=0)
    executed_qty: Optional[int] = Field(None, gt=0)


class OrderSchema(OrderBase):
    id: str
    user_id: int
    executed_price: Optional[float] = None
    executed_qty: Optional[int] = None
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Strategy Schemas ====================

class StrategyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    index: str
    status: StrategyStatusEnum = StrategyStatusEnum.ACTIVE
    description: Optional[str] = None
    profit_target: Optional[float] = None
    stop_loss: Optional[float] = None


class StrategyCreate(StrategyBase):
    pass


class StrategyUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    status: Optional[StrategyStatusEnum] = None
    description: Optional[str] = None
    profit_target: Optional[float] = None
    stop_loss: Optional[float] = None


class StrategySchema(StrategyBase):
    id: int
    user_id: int
    current_pnl: float
    trades: int
    win_rate: float
    entry_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Alert Schemas ====================

class AlertSchema(BaseModel):
    id: Optional[int] = None
    message: str
    alert_type: AlertTypeEnum
    timestamp: Optional[datetime] = None
    is_read: bool = False

    class Config:
        from_attributes = True


class AlertCreate(BaseModel):
    message: str
    alert_type: AlertTypeEnum


class AlertUpdate(BaseModel):
    is_read: Optional[bool] = None


# ==================== Log Schemas ====================

class LogSchema(BaseModel):
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    level: LogLevelEnum
    message: str
    category: Optional[str] = None
    source: Optional[str] = None
    user_id: Optional[int] = None
    metadata: Optional[str] = None

    class Config:
        from_attributes = True


class LogCreate(BaseModel):
    level: LogLevelEnum
    message: str
    category: Optional[str] = None
    source: Optional[str] = None
    user_id: Optional[int] = None
    metadata: Optional[str] = None


# ==================== Analytics Schemas ====================

class AnalyticsSchema(BaseModel):
    id: Optional[int] = None
    date: str  # YYYY-MM-DD
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0
    total_pnl: float = 0
    average_win: float = 0
    average_loss: float = 0
    profit_factor: float = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnalyticsCreate(BaseModel):
    date: str
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0


# ==================== Generic Response Schemas ====================

T = TypeVar('T')


class ResponseSchema(BaseModel, Generic[T]):
    """Generic response wrapper for successful responses"""
    data: Optional[T] = None
    status: int = 200
    message: Optional[str] = None

    class Config:
        from_attributes = True


class ErrorResponseSchema(BaseModel):
    """Error response wrapper"""
    message: str
    status: int
    data: Optional[Any] = None
    details: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== Authentication Schemas ====================

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class LoginResponseSchema(BaseModel):
    access_token: str
    token_type: str
    user: UserSchema


# ==================== Pagination Schemas ====================

class PaginationSchema(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
    total: Optional[int] = None
    total: Optional[int] = None
    total_pages: Optional[int] = None
    total: Optional[int] = None
    total_pages: Optional[int] = None
#     gender: Optional[str] = None

#     is_subscribe: Optional[bool] = None
