"""
Database models for Nifties API
All models are defined here with proper relationships and constraints
"""

from app.db.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, Numeric, Text
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")  # admin, user, trader
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trades = relationship("Trade", back_populates="user")
    orders = relationship("Order", back_populates="user")
    strategies = relationship("Strategy", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class MarketIndex(Base):
    """Market indices tracking (NIFTY 50, BANKNIFTY, etc.)"""
    __tablename__ = 'market_indices'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    value = Column(Numeric(10, 2), nullable=False)
    change = Column(Numeric(10, 2), nullable=False)
    change_percent = Column(Numeric(5, 2), nullable=False)
    is_positive = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MarketIndex(name={self.name}, value={self.value})>"


class PnL(Base):
    """Profit & Loss tracking for different periods"""
    __tablename__ = 'pnl'
    
    id = Column(Integer, primary_key=True, index=True)
    period = Column(String(20), nullable=False)  # today, week, month
    value = Column(Numeric(12, 2), nullable=False)
    is_positive = Column(Boolean, default=True)
    description = Column(String(255))
    trades = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PnL(period={self.period}, value={self.value})>"


class Trade(Base):
    """Options trading records"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    symbol = Column(String(50), nullable=False)  # e.g., "NIFTY 21900 CE"
    index = Column(String(20), nullable=False)  # NIFTY, BANKNIFTY, etc.
    strike = Column(Integer, nullable=False)
    type = Column(String(2), nullable=False)  # CE or PE
    qty = Column(Integer, nullable=False)
    entry_price = Column(Numeric(10, 2), nullable=False)
    current_price = Column(Numeric(10, 2), nullable=False)
    pnl = Column(Numeric(12, 2), default=0)
    pnl_percent = Column(Numeric(5, 2), default=0)
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, CLOSED, PENDING
    strategy = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="trades")
    
    def __repr__(self):
        return f"<Trade(id={self.id}, symbol={self.symbol}, status={self.status})>"


class Order(Base):
    """Order history and management"""
    __tablename__ = 'orders'
    
    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    symbol = Column(String(50), nullable=False)
    order_type = Column(String(10), nullable=False)  # BUY, SELL
    qty = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), nullable=False)  # PENDING, COMPLETED, CANCELLED, REJECTED
    executed_price = Column(Numeric(10, 2))
    executed_qty = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.id}, symbol={self.symbol}, status={self.status})>"


class Strategy(Base):
    """Trading strategies"""
    __tablename__ = 'strategies'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    index = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, INACTIVE, COMPLETED
    description = Column(Text)
    entry_date = Column(DateTime, default=datetime.utcnow)
    profit_target = Column(Numeric(12, 2))
    stop_loss = Column(Numeric(12, 2))
    current_pnl = Column(Numeric(12, 2), default=0)
    trades = Column(Integer, default=0)
    win_rate = Column(Numeric(5, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="strategies")
    
    def __repr__(self):
        return f"<Strategy(id={self.id}, name={self.name}, status={self.status})>"


class Alert(Base):
    """Alerts and notifications"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String(500), nullable=False)
    alert_type = Column(String(20), nullable=False)  # success, warning, error, info
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type})>"


class Log(Base):
    """System and activity logs"""
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    category = Column(String(50))  # STRATEGY, TRADE, ORDER, SYSTEM
    source = Column(String(100))  # AlgoEngine, RiskManager, etc.
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    metadata = Column(Text)  # JSON for additional data
    
    def __repr__(self):
        return f"<Log(id={self.id}, level={self.level}, category={self.category})>"


class Analytics(Base):
    """Trading analytics and statistics"""
    __tablename__ = 'analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), nullable=False, unique=True, index=True)  # YYYY-MM-DD
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Numeric(5, 2), default=0)
    total_pnl = Column(Numeric(12, 2), default=0)
    average_win = Column(Numeric(10, 2), default=0)
    average_loss = Column(Numeric(10, 2), default=0)
    profit_factor = Column(Numeric(5, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Analytics(date={self.date}, total_trades={self.total_trades})>"
