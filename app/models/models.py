"""
Complete Database Models for Nifty Algo Trading Platform
All models with proper relationships, constraints, and indexes
Version: 2.0 - Cleaned and Optimized
"""

from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, 
    Float, Boolean, Numeric, Text, Index, UniqueConstraint,
    Enum as SQLEnum, JSON ,BigInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.sql import func
import enum

Base = declarative_base()


# ==================== ENUMS ====================
class UserRole(str, enum.Enum):
    SUPERADMIN = "SUPERADMIN"
    ADMIN = "ADMIN"
    TRADER = "TRADER"
    USER = "USER"


class OrderType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PLACED = "PLACED"
    EXECUTED = "EXECUTED"
    PARTIALLY_EXECUTED = "PARTIALLY_EXECUTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class PositionStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class StrategyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"


class SignalType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    EXIT = "EXIT"
    HOLD = "HOLD"


class AlertType(str, enum.Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"


class LogLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CloseTypeEnum(str, enum.Enum):
    NIFTIES = "NIFTIES"
    EQUITIES = "EQUITIES"
    BUY_NIFTIES = "BUY_NIFTIES"
    SELL_NIFTIES = "SELL_NIFTIES"
    CE = "CE"
    PE = "PE"
    ALL = "ALL"


class CloseForEnum(str, enum.Enum):
    NIFTY = "NIFTY"
    BANKNIFTY = "BANKNIFTY"
    FINNIFTY = "FINNIFTY"
    MIDCPNIFTY = "MIDCPNIFTY"
    SENSEX = "SENSEX"
    BANKEX = "BANKEX"
    ALL = "ALL"


class ExchangeEnum(str,enum.Enum):
    NSE = "NSE"        # National Stock Exchange (Equity Cash)
    BSE = "BSE"        # Bombay Stock Exchange (Equity Cash)
    NFO = "NFO"        # NSE F&O (Index & Stock Derivatives)
    BFO = "BFO"        # BSE F&O (less commonly used)
    CDS = "CDS"        # NSE Currency (USDINR, EURINR)
    BCD = "BCD"        # BSE Currency
    MCX = "MCX"        # Multi Commodity Exchange (Gold, Silver, Crude, NG)
    ALL = "ALL"        # All exchanges combined (internal use)
    NSE_IDX = "NSE_IDX"    # Index quotes (internal classification)
    BSE_IDX = "BSE_IDX"
    SGX = "SGX"            # Singapore Exchange (NIFTY futures - now GIFT)
    GIFT = "GIFT"          # NSE IFSC at GIFT City (International F&O)


class InstrumentType(str,enum.Enum):
    EQUITY = "EQUITY"          # Cash market stock (EQ)
    ETF = "ETF"                # Exchange Traded Fund
    INDEX = "INDEX"            # NIFTY, BANKNIFTY, FINNIFTY
    FUT_INDEX = "FUTIDX"       # Index Future
    FUT_STOCK = "FUTSTK"       # Stock Future
    FUT_CURRENCY = "FUTCUR"    # Currency Future
    FUT_COMMODITY = "FUTCOM"   # Commodity Future
    OPT_INDEX = "OPTIDX"       # Index Option
    OPT_STOCK = "OPTSTK"       # Stock Option
    OPT_CURRENCY = "OPTCUR"    # Currency Option
    OPT_COMMODITY = "OPTCOM"   # Commodity Option
    CURRENCY_PAIR = "CURRENCY" # USDINR, EURINR, GBPINR, JPYINR
    COMMODITY = "COMMODITY"    # MCX products like GOLD, SILVER
    BOND = "BOND"              # Government/Corporate Bonds
    DEBENTURE = "DEBENTURE"
    MUTUAL_FUND = "MF"         # Mutual Funds
    WARRANT = "WARRANT"
    SGB = "SGB"                # Sovereign Gold Bond


class TimeFrame(str,enum.Enum):
    FIVE_SEC="5_SEC"
    TEN_SEC="10_SEC"
    FIFTEEN_SEC="15_SEC"
    THIRTY_SEC="30_SEC"
    ONE_MIN="1_MIN"
    THREE_MIN="3_MIN"
    FIVE_MIN="5_MIN"
    FIFTEEN_MIN="15_MIN"
    THIRTY_MIN="30_MIN"
    SIXTY_MIN="60_MIN"
    ONE_DAY="1_DAY"





# ==================== USER MANAGEMENT ====================

class Broker(Base):
    """Broker Master Table - All supported brokers"""
    __tablename__ = "brokers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(String(255))
    
    # API Configuration
    api_base_url = Column(String(255))
    supports_websocket = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # user_accounts = relationship("UserBrokerAccount", back_populates="broker")
    
    def __repr__(self):
        return f"<Broker(id={self.id}, name={self.name})>"


class User(Base):
    """User model for authentication and profile management"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True)

    # Role and Status
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.TRADER)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    kyc_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    # broker_accounts = relationship("UserBrokerAccount", back_populates="user", cascade="all, delete-orphan")
    angel_credentials = relationship("AngelOneCredentials", back_populates="user", uselist=False, cascade="all, delete-orphan")
    dhan_credentials = relationship("DhanCredentials", back_populates="user", uselist=False, cascade="all, delete-orphan")
    trading_settings = relationship("UserTradingSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    risk_settings = relationship("UserRiskSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    ui_settings = relationship("UserUISettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # positions = relationship("Position", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    # strategies = relationship("Strategy", back_populates="user", cascade="all, delete-orphan")
    risk_metrics = relationship("RiskMetrics", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    pnl_snapshots = relationship("PnLSnapshot", back_populates="user", cascade="all, delete-orphan")
    backtests = relationship("Backtest", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


# class UserBrokerAccount(Base):
#     """User's Broker Account Configuration"""
#     __tablename__ = "user_broker_accounts"
# 
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False, index=True)
#     broker_id = Column(Integer, ForeignKey("brokers.id"), nullable=False, index=True)
# 
#     # Broker Credentials
#     broker_client_id = Column(String(100), nullable=False)
#     api_key = Column(String(500))  # Encrypted
#     api_secret = Column(String(500))  # Encrypted
#     access_token = Column(String(500))  # Encrypted
#     refresh_token = Column(String(500))  # Encrypted
#     
#     # Session Management
#     session_token = Column(String(500))
#     token_expires_at = Column(DateTime(timezone=True))
#     last_synced_at = Column(DateTime(timezone=True))
#     
#     # Account Status
#     is_active = Column(Boolean, default=False, index=True)
#     is_connected = Column(Boolean, default=False)
#     
#     # Account Balance
#     account_balance = Column(Numeric(12, 2), default=0)
#     margin_available = Column(Numeric(12, 2), default=0)
#     margin_used = Column(Numeric(12, 2), default=0)
#     
#     # Timestamps
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
# 
#     # Relationships
#     user = relationship("User", back_populates="broker_accounts")
#     broker = relationship("Broker", back_populates="user_accounts")
# 
#     __table_args__ = (
#         UniqueConstraint("user_id", "broker_id", name="uq_user_broker"),
#         Index('idx_user_broker_active', 'user_id', 'is_active'),
#     )
#     
#     def __repr__(self):
#         return f"<UserBrokerAccount(id={self.id}, user_id={self.user_id}, broker_id={self.broker_id})>"


class AngelOneCredentials(Base):
    __tablename__ = "angelone_credentials"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Common
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Angel One specific
    name = Column(String(100), nullable=True)
    email = Column(String(150), nullable=False)
    api_key = Column(Text, nullable=False)
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    token = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="angel_credentials")

    def __repr__(self):
        return f"<AngelOneCredentials user_id={self.user_id} active={self.is_active}>"


class DhanCredentials(Base):
    __tablename__ = "dhan_credentials"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Common
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Dhan specific
    name = Column(String(100), nullable=True)
    email = Column(String(150), nullable=False)
    client_id = Column(Text, nullable=False)
    access_token = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="dhan_credentials")

    def __repr__(self):
        return f"<DhanCredentials user_id={self.user_id} active={self.is_active}>"


class UserTradingSettings(Base):
    """User Trading Preferences and Configuration"""
    __tablename__ = "user_trading_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), unique=True, nullable=False)

    # Trading Preferences
    timezone = Column(String(50), default="Asia/Kolkata")
    auto_square_off = Column(Boolean, default=True)
    auto_square_off_time = Column(String(10), default="15:20")  # HH:MM format
    
    # Default Order Settings
    default_qty = Column(Integer, default=1)
    default_product_type = Column(String(20), default="NRML")  # MIS, NRML, CNC
    default_order_type = Column(String(20), default="MARKET")  # MARKET, LIMIT
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="trading_settings")
    
    def __repr__(self):
        return f"<UserTradingSettings(user_id={self.user_id}, timezone={self.timezone})>"


class UserRiskSettings(Base):
    """User Risk Management Settings"""
    __tablename__ = "user_risk_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), unique=True, nullable=False)

    # Position Limits
    max_position_size = Column(Numeric(12, 2), default=100000)
    max_positions = Column(Integer, default=10)
    max_positions_per_symbol = Column(Integer, default=3)
    
    # Loss Limits
    daily_loss_limit = Column(Numeric(12, 2), default=10000)
    weekly_loss_limit = Column(Numeric(12, 2), default=30000)
    monthly_loss_limit = Column(Numeric(12, 2), default=100000)
    
    # Risk Parameters
    risk_per_trade = Column(Numeric(5, 2), default=2.0)  # Percentage
    max_drawdown_limit = Column(Numeric(5, 2), default=20.0)  # Percentage
    
    # Auto Actions
    stop_trading_on_limit = Column(Boolean, default=True)
    emergency_exit_on_limit = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="risk_settings")
    
    def __repr__(self):
        return f"<UserRiskSettings(user_id={self.user_id}, daily_limit={self.daily_loss_limit})>"


class UserUISettings(Base):
    """User UI/UX Preferences"""
    __tablename__ = "user_ui_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), unique=True, nullable=False)

    # Display Preferences
    theme = Column(String(20), default='light')  # light, dark, auto
    language = Column(String(10), default='en')
    
    # Notification Preferences
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    trade_notifications = Column(Boolean, default=True)
    order_notifications = Column(Boolean, default=True)
    risk_notifications = Column(Boolean, default=True)
    
    # Dashboard Preferences
    dashboard_layout = Column(JSON)  # Custom dashboard configuration
    favorite_symbols = Column(JSON)  # List of favorite symbols
    chart_preferences = Column(JSON)  # Chart settings
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="ui_settings")
    
    def __repr__(self):
        return f"<UserUISettings(user_id={self.user_id}, theme={self.theme})>"


# ==================== MARKET DATA ====================

class MarketIndex(Base):
    """Market indices tracking (NIFTY 50, BANK NIFTY, etc.)"""
    __tablename__ = 'market_indices'
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    
    # Price Data
    ltp = Column(Numeric(10, 2), nullable=False)  # Last traded price
    open_price = Column(Numeric(10, 2))
    high = Column(Numeric(10, 2))
    low = Column(Numeric(10, 2))
    close = Column(Numeric(10, 2))
    prev_close = Column(Numeric(10, 2))
    
    # Change
    change = Column(Numeric(10, 2))
    change_percent = Column(Numeric(5, 2))
    
    # Volume
    volume = Column(Integer, default=0)
    
    # Status
    is_trading = Column(Boolean, default=True, index=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<MarketIndex(symbol={self.symbol}, ltp={self.ltp})>"


class OptionChain(Base):
    """Options chain data for different strikes and expiries"""
    __tablename__ = 'option_chain'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Option Details
    underlying = Column(String(50), nullable=False, index=True)  # NIFTY, BANKNIFTY
    symbol = Column(String(100), nullable=False, unique=True, index=True)
    expiry_date = Column(DateTime(timezone=True), nullable=False, index=True)
    strike_price = Column(Integer, nullable=False, index=True)
    option_type = Column(String(2), nullable=False)  # CE or PE
    
    # Price Data
    ltp = Column(Numeric(10, 2))
    bid_price = Column(Numeric(10, 2))
    ask_price = Column(Numeric(10, 2))
    open_price = Column(Numeric(10, 2))
    high = Column(Numeric(10, 2))
    low = Column(Numeric(10, 2))
    close = Column(Numeric(10, 2))
    prev_close = Column(Numeric(10, 2))
    
    # Volume and OI
    volume = Column(Integer, default=0)
    open_interest = Column(Integer, default=0)
    oi_change = Column(Integer, default=0)
    oi_change_percent = Column(Numeric(5, 2))
    
    # Greeks
    iv = Column(Numeric(6, 2))  # Implied Volatility
    delta = Column(Numeric(8, 6))
    gamma = Column(Numeric(8, 6))
    theta = Column(Numeric(8, 6))
    vega = Column(Numeric(8, 6))
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_option_lookup', 'underlying', 'expiry_date', 'strike_price', 'option_type'),
        Index('idx_option_expiry_strike', 'expiry_date', 'strike_price'),
        Index('idx_option_updated', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<OptionChain(symbol={self.symbol}, ltp={self.ltp})>"


class HistoricalData(Base):
    """Historical price data for backtesting"""
    __tablename__ = 'historical_data'
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(100), nullable=False, index=True)
    # timeframe = Column(String(10), nullable=False)  # 1m, 5m, 15m, 1h, 1d
    timeframe = Column(SQLEnum(TimeFrame), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # OHLCV Data
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(Integer, default=0)
    
    __table_args__ = (
        UniqueConstraint('symbol', 'timeframe', 'timestamp', name='uq_historical_data'),
        Index('idx_historical_symbol_time', 'symbol', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<HistoricalData(symbol={self.symbol}, timeframe={self.timeframe})>"


# ==================== TRADING ====================

class Position(Base):
    """Current open positions"""
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    # strategy_id = Column(Integer, ForeignKey('strategies.id', ondelete='SET NULL'))
    
    # # Position Details
    # symbol = Column(String(100), nullable=False, index=True)
    # underlying = Column(String(50), nullable=False, index=True)
    # strike_price = Column(Integer, nullable=False)
    # option_type = Column(String(2), nullable=False)  # CE/PE
    # expiry_date = Column(DateTime(timezone=True), nullable=False)
    
    # # Quantity and Pricing
    # qty = Column(Integer, nullable=False)
    # avg_entry_price = Column(Numeric(10, 2), nullable=False)
    # avg_exit_price = Column(Numeric(10, 2),default=0 )
    
    # # P&L
    # realized_pnl = Column(Numeric(12, 2), default=0)
    # unrealized_pnl = Column(Numeric(12, 2), default=0)
    # total_pnl = Column(Numeric(12, 2), default=0)
    # pnl_percent = Column(Numeric(6, 2), default=0)
    
    # # Risk Management
    # stop_loss = Column(Numeric(10, 2))
    # target = Column(Numeric(10, 2))
    # trailing_sl = Column(Boolean, default=False)
    # trailing_sl_percent = Column(Numeric(5, 2))
    
    # # Margin
    # margin_used = Column(Numeric(12, 2))
    
    # # Status
    # status = Column(SQLEnum(PositionStatus), nullable=False, default=PositionStatus.OPEN, index=True)
    
    # # Timestamps
    # entry_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # exit_time = Column(DateTime(timezone=True))
    # updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # # Relationships
    # user = relationship("User", back_populates="positions")
    # strategy = relationship("Strategy", back_populates="positions")
    
    # __table_args__ = (
    #     Index('idx_position_user_status', 'user_id', 'status'),
    #     Index('idx_position_symbol_status', 'symbol', 'status'),
    #     Index('idx_position_underlying', 'underlying', 'status'),
    # )
    
    def __repr__(self):
        return f"<Position(id={self.id})>"


class Order(Base):
    """Order history and management"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    signal_log_id = Column(BigInteger, ForeignKey('signal_logs.id', ondelete='SET NULL'), index=True)
    strategy_id = Column(Integer, ForeignKey('strategies.id', ondelete='SET NULL'), index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Order Details
    symbol = Column(String(100), nullable=False, index=True)
    option_type = Column(String(2))  # PE or CE
    
    # Price and Quantity
    entry_price = Column(Numeric(10, 2))
    exit_price = Column(Numeric(10, 2))
    qty = Column(Integer, nullable=False)
    
    # Status
    status = Column(String(50), default='PENDING', index=True)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Timestamps
    entry_time = Column(DateTime(timezone=True))
    exit_time = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="orders")
    signal_log = relationship("SignalLog", back_populates="orders")
    strategy = relationship("Strategy", back_populates="orders")
    broker_order = relationship("BrokerOrder", back_populates="order", uselist=False)
    __table_args__ = (
        Index('idx_order_user_status', 'user_id', 'status'),
        
    )
    
    def __repr__(self):
        return f"<Order(id={self.id}, symbol={self.symbol}, status={self.status})>"


class Trade(Base):
    """Completed trades history"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, index=True)
    # user_id removed - Trade is now a master signal record
    strategy_id = Column(Integer, ForeignKey('strategies.id', ondelete='SET NULL'), index=True)
    # position_id = Column(Integer, ForeignKey('positions.id', ondelete='SET NULL'))
    signal_id = Column(BigInteger, ForeignKey('signal_logs.id', ondelete='SET NULL'), index=True)
    
    # Trade Details
    symbol = Column(String(100), nullable=False, index=True)
    underlying = Column(String(50), nullable=False, index=True)
    strike_price = Column(Integer, nullable=False)
    option_type = Column(String(2), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    
    # Entry
    entry_qty = Column(Integer, nullable=False)
    entry_price = Column(Numeric(10, 2), nullable=False)
    entry_time = Column(DateTime(timezone=True), nullable=False, index=True)
    entry_order_id = Column(String(100))
    
    # Exit
    exit_qty = Column(Integer, nullable=False)
    exit_price = Column(Numeric(10, 2), nullable=False)
    exit_time = Column(DateTime(timezone=True), nullable=False)
    exit_order_id = Column(String(100))
    
    # P&L
    gross_pnl = Column(Numeric(12, 2), nullable=False)
    brokerage = Column(Numeric(10, 2), default=0)
    taxes = Column(Numeric(10, 2), default=0)
    charges = Column(Numeric(10, 2), default=0)
    net_pnl = Column(Numeric(12, 2), nullable=False)
    pnl_percent = Column(Numeric(6, 2))
    
    # Trade Metadata
    trade_type = Column(String(20))  # INTRADAY, POSITIONAL
    exit_reason = Column(String(50))  # TARGET, STOPLOSS, MANUAL, SQUARE_OFF, EXPIRY
    holding_time = Column(Integer)  # in minutes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="trades")
    # position = relationship("Position", foreign_keys=[position_id])
    
    __table_args__ = (
        Index('idx_trade_symbol', 'symbol', 'entry_time'),
        Index('idx_trade_underlying', 'underlying', 'entry_time'),
        Index('idx_trade_strategy', 'strategy_id', 'entry_time'),
    )
    
    def __repr__(self):
        return f"<Trade(id={self.id}, symbol={self.symbol}, pnl={self.net_pnl})>"


# ==================== STRATEGY ====================

class Strategy(Base):
    """Trading strategies and algorithms"""
    __tablename__ = 'strategies'
    
    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Strategy Details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    # strategy_type = Column(String(50))  # MOMENTUM, MEAN_REVERSION, ARBITRAGE, STRADDLE, etc.
    underlying = Column(String(50), nullable=False, index=True)  # NIFTY, BANKNIFTY
    
    # Configuration
    # config = Column(JSON)  # Strategy-specific parameters
    timeframe = Column(String(10))  # 1m, 5m, 15m, 1h, 1d
    
    # Risk Management
    # max_positions = Column(Integer, default=1)
    # position_size = Column(Numeric(12, 2))
    # stop_loss_pct = Column(Numeric(5, 2))
    # target_pct = Column(Numeric(5, 2))
    # max_loss_per_day = Column(Numeric(12, 2))
    
    # # Status
    # status = Column(SQLEnum(StrategyStatus), nullable=False, default=StrategyStatus.ACTIVE, index=True)
    is_live = Column(Boolean, default=False, index=True)
    
    # Performance
    # total_trades = Column(Integer, default=0)
    # winning_trades = Column(Integer, default=0)
    # losing_trades = Column(Integer, default=0)
    # win_rate = Column(Numeric(5, 2), default=0)
    # total_pnl = Column(Numeric(12, 2), default=0)
    # max_drawdown = Column(Numeric(12, 2), default=0)
    # sharpe_ratio = Column(Numeric(6, 4))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # started_at = Column(DateTime(timezone=True))
    # stopped_at = Column(DateTime(timezone=True))
    
    # Relationships
    # user = relationship("User", back_populates="strategies")
    # positions = relationship("Position", back_populates="strategy")
    orders = relationship("Order", back_populates="strategy")
    trades = relationship("Trade", back_populates="strategy")
    # orders = relationship("Order", back_populates="trade") # Added relationship in Order, need back_populates here

    signals = relationship("Signal", back_populates="strategy", cascade="all, delete-orphan")
    
    # __table_args__ = (
    #     Index('idx_strategy_user_status', 'user_id', 'status'),
    #     Index('idx_strategy_underlying', 'underlying', 'status'),
    # )
    
    def __repr__(self):
        return f"<Strategy(id={self.id}, name={self.name})>"


class Signal(Base):
    """Trading signals generated by strategies"""
    __tablename__ = 'signals'
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey('strategies.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Signal Details
    signal_type = Column(SQLEnum(SignalType), nullable=False)
    symbol = Column(String(100), nullable=False, index=True)
    underlying = Column(String(50), nullable=False, index=True)
    strike_price = Column(Integer)
    option_type = Column(String(2))
    
    # Price and Quantity
    price = Column(Numeric(10, 2))
    qty = Column(Integer)
    
    # Signal Metadata
    confidence = Column(Numeric(5, 2))  # 0-100
    reason = Column(Text)
    indicators = Column(JSON)  # Technical indicators data
    
    # Status
    status = Column(String(20), default='PENDING', index=True)  # PENDING, EXECUTED, EXPIRED, IGNORED
    
    # Execution
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='SET NULL'))
    executed_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    strategy = relationship("Strategy", back_populates="signals")
    order = relationship("Order", foreign_keys=[order_id])
    
    __table_args__ = (
        Index('idx_signal_strategy_status', 'strategy_id', 'status'),
        Index('idx_signal_created', 'created_at'),
        Index('idx_signal_underlying', 'underlying', 'status'),
    )
    
    def __repr__(self):
        return f"<Signal(id={self.id}, type={self.signal_type}, symbol={self.symbol})>"


# ==================== RISK & ANALYTICS ====================

class RiskMetrics(Base):
    """Daily risk metrics and exposure tracking"""
    __tablename__ = 'risk_metrics'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Exposure
    total_capital = Column(Numeric(12, 2))
    total_exposure = Column(Numeric(12, 2))
    margin_available = Column(Numeric(12, 2))
    margin_used = Column(Numeric(12, 2))
    margin_utilization_pct = Column(Numeric(5, 2))
    
    # P&L
    daily_pnl = Column(Numeric(12, 2), default=0)
    unrealized_pnl = Column(Numeric(12, 2), default=0)
    realized_pnl = Column(Numeric(12, 2), default=0)
    
    # Risk Metrics
    max_drawdown = Column(Numeric(12, 2), default=0)
    var_95 = Column(Numeric(12, 2))  # Value at Risk
    portfolio_delta = Column(Numeric(10, 4))
    portfolio_gamma = Column(Numeric(10, 4))
    portfolio_theta = Column(Numeric(10, 4))
    portfolio_vega = Column(Numeric(10, 4))
    
    # Limits
    limit_breach_count = Column(Integer, default=0)
    risk_alert_level = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="risk_metrics")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uq_risk_metrics_user_date'),
        Index('idx_risk_user_date', 'user_id', 'date'),
    )
    
    def __repr__(self):
        return f"<RiskMetrics(user_id={self.user_id}, date={self.date}, daily_pnl={self.daily_pnl})>"


class Analytics(Base):
    """Trading analytics and performance statistics"""
    __tablename__ = 'analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    strategy_id = Column(Integer, ForeignKey('strategies.id', ondelete='CASCADE'))
    
    # Time Period
    period_type = Column(String(20), nullable=False, index=True)  # DAILY, WEEKLY, MONTHLY, YEARLY
    period_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Trade Statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    breakeven_trades = Column(Integer, default=0)
    
    # Win Rate
    win_rate = Column(Numeric(5, 2), default=0)
    loss_rate = Column(Numeric(5, 2), default=0)
    
    # P&L Statistics
    total_pnl = Column(Numeric(12, 2), default=0)
    avg_profit = Column(Numeric(10, 2), default=0)
    avg_loss = Column(Numeric(10, 2), default=0)
    largest_win = Column(Numeric(12, 2), default=0)
    largest_loss = Column(Numeric(12, 2), default=0)
    
    # Risk Metrics
    profit_factor = Column(Numeric(6, 2), default=0)
    sharpe_ratio = Column(Numeric(6, 4))
    max_drawdown = Column(Numeric(12, 2), default=0)
    recovery_factor = Column(Numeric(6, 2))
    
    # Expectancy
    expectancy = Column(Numeric(10, 2))
    risk_reward_ratio = Column(Numeric(6, 2))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'strategy_id', 'period_type', 'period_date', 
                        name='uq_analytics_period'),
        Index('idx_analytics_period', 'period_type', 'period_date'),
    )
    
    def __repr__(self):
        return f"<Analytics(period={self.period_type}, date={self.period_date}, pnl={self.total_pnl})>"


# ==================== NOTIFICATIONS & ALERTS ====================

class Notification(Base):
    """User notifications and alerts"""
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Notification Details
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(SQLEnum(AlertType), nullable=False)
    category = Column(String(50), index=True)  # TRADE, ORDER, RISK, SYSTEM, STRATEGY
    
    # Related Entity
    related_entity_type = Column(String(50))  # ORDER, TRADE, POSITION, STRATEGY
    related_entity_id = Column(Integer)
    
    # Status
    is_read = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False)
    
    # Priority
    priority = Column(String(20), default="NORMAL")  # LOW, NORMAL, HIGH, URGENT
    
    # Delivery
    sent_via_email = Column(Boolean, default=False)
    sent_via_sms = Column(Boolean, default=False)
    sent_via_push = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    read_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    __table_args__ = (
        Index('idx_notification_user_read', 'user_id', 'is_read'),
        Index('idx_notification_created', 'created_at'),
        Index('idx_notification_category', 'category', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type}, read={self.is_read})>"


class Alert(Base):
    """Price alerts and conditional notifications"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Alert Details
    name = Column(String(100), nullable=False)
    symbol = Column(String(100), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # PRICE_ABOVE, PRICE_BELOW, PERCENT_CHANGE
    
    # Conditions
    condition_price = Column(Numeric(10, 2))
    condition_percent = Column(Numeric(5, 2))
    current_price = Column(Numeric(10, 2))
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_triggered = Column(Boolean, default=False)
    trigger_once = Column(Boolean, default=True)
    
    # Notification Preferences
    notify_email = Column(Boolean, default=False)
    notify_sms = Column(Boolean, default=False)
    notify_push = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    triggered_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_alert_user_active', 'user_id', 'is_active'),
        Index('idx_alert_symbol_active', 'symbol', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Alert(id={self.id}, symbol={self.symbol}, type={self.alert_type})>"


# ==================== WATCHLIST ====================

class Watchlist(Base):
    """User watchlists for tracking symbols"""
    __tablename__ = 'watchlists'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Watchlist Details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="watchlists")
    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_watchlist_user', 'user_id'),
    )
    
    def __repr__(self):
        return f"<Watchlist(id={self.id}, name={self.name})>"


class WatchlistItem(Base):
    """Individual items in a watchlist"""
    __tablename__ = 'watchlist_items'
    
    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey('watchlists.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Symbol Details
    symbol = Column(String(100), nullable=False, index=True)
    underlying = Column(String(50))
    strike_price = Column(Integer)
    option_type = Column(String(2))
    expiry_date = Column(DateTime(timezone=True))
    
    # Display Order
    sort_order = Column(Integer, default=0)
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    watchlist = relationship("Watchlist", back_populates="items")
    
    __table_args__ = (
        UniqueConstraint('watchlist_id', 'symbol', name='uq_watchlist_symbol'),
        Index('idx_watchlist_item', 'watchlist_id', 'sort_order'),
    )
    
    def __repr__(self):
        return f"<WatchlistItem(id={self.id}, symbol={self.symbol})>"


# ==================== SYSTEM & LOGGING ====================

class SystemLog(Base):
    """System and activity logs"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Log Details
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    level = Column(SQLEnum(LogLevel), nullable=False, index=True)
    category = Column(String(50), index=True)  # STRATEGY, TRADE, ORDER, SYSTEM, AUTH
    source = Column(String(100))  # Component/Service name
    
    # Message
    message = Column(Text, nullable=False)
    
    # Context
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    strategy_id = Column(Integer, ForeignKey('strategies.id', ondelete='SET NULL'))
    
    # Additional Data
    log_metadata = Column(JSON)  # Additional context as JSON
    
    # Error Details
    error_code = Column(String(50))
    stack_trace = Column(Text)
    
    __table_args__ = (
        Index('idx_log_timestamp_level', 'timestamp', 'level'),
        Index('idx_log_category', 'category', 'timestamp'),
        Index('idx_log_user', 'user_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SystemLog(id={self.id}, level={self.level}, category={self.category})>"


class AuditLog(Base):
    """Audit trail for critical actions"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Actor
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), index=True)
    username = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Action
    action = Column(String(100), nullable=False, index=True)  # LOGIN, ORDER_PLACED, STRATEGY_STARTED
    resource_type = Column(String(50))  # USER, ORDER, POSITION, STRATEGY
    resource_id = Column(String(100))
    
    # Details
    description = Column(Text)
    old_value = Column(JSON)
    new_value = Column(JSON)
    
    # Status
    status = Column(String(20))  # SUCCESS, FAILURE
    error_message = Column(Text)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_action', 'action', 'timestamp'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user={self.username})>"


# ==================== BROKER INTEGRATION ====================

class BrokerOrder(Base):
    """Raw broker order responses for reconciliation"""
    __tablename__ = 'broker_orders'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='SET NULL'), unique=True)
    
    # Broker Details
    broker_order_id = Column(String(100), unique=True, index=True)
    exchange_order_id = Column(String(100))
    
    # Raw Response
    raw_response = Column(JSON)  # Complete broker API response
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="broker_order")
    
    __table_args__ = (
        Index('idx_broker_order_user', 'user_id', 'broker_order_id'),
    )
    
    def __repr__(self):
        return f"<BrokerOrder(id={self.id}, broker_order_id={self.broker_order_id})>"


# ==================== BACKTESTING ====================

class Backtest(Base):
    """Backtesting results and simulations"""
    __tablename__ = 'backtests'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    strategy_id = Column(Integer, ForeignKey('strategies.id', ondelete='SET NULL'))
    
    # Backtest Details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Parameters
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    initial_capital = Column(Numeric(12, 2), nullable=False)
    
    # Configuration
    config = Column(JSON)  # Strategy parameters used
    
    # Results
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Numeric(5, 2), default=0)
    
    # P&L
    total_pnl = Column(Numeric(12, 2), default=0)
    total_return_pct = Column(Numeric(6, 2), default=0)
    avg_profit = Column(Numeric(10, 2), default=0)
    avg_loss = Column(Numeric(10, 2), default=0)
    
    # Risk Metrics
    max_drawdown = Column(Numeric(12, 2), default=0)
    max_drawdown_pct = Column(Numeric(6, 2), default=0)
    sharpe_ratio = Column(Numeric(6, 4))
    sortino_ratio = Column(Numeric(6, 4))
    calmar_ratio = Column(Numeric(6, 4))
    profit_factor = Column(Numeric(6, 2))
    
    # Execution Stats
    status = Column(String(20), default='COMPLETED', index=True)  # RUNNING, COMPLETED, FAILED
    execution_time = Column(Integer)  # in seconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="backtests")
    trades = relationship("BacktestTrade", back_populates="backtest", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_backtest_user', 'user_id', 'created_at'),
        Index('idx_backtest_strategy', 'strategy_id'),
    )
    
    def __repr__(self):
        return f"<Backtest(id={self.id}, name={self.name}, return={self.total_return_pct}%)>"


class BacktestTrade(Base):
    """Individual trades from backtesting"""
    __tablename__ = 'backtest_trades'
    
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey('backtests.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Trade Details
    symbol = Column(String(100), nullable=False)
    entry_time = Column(DateTime(timezone=True), nullable=False)
    exit_time = Column(DateTime(timezone=True), nullable=False)
    
    # Entry
    entry_price = Column(Numeric(10, 2), nullable=False)
    qty = Column(Integer, nullable=False)
    
    # Exit
    exit_price = Column(Numeric(10, 2), nullable=False)
    exit_reason = Column(String(50))
    
    # P&L
    pnl = Column(Numeric(12, 2), nullable=False)
    pnl_percent = Column(Numeric(6, 2))
    
    # Relationships
    backtest = relationship("Backtest", back_populates="trades")
    
    __table_args__ = (
        Index('idx_backtest_trade', 'backtest_id', 'entry_time'),
    )
    
    def __repr__(self):
        return f"<BacktestTrade(id={self.id}, symbol={self.symbol}, pnl={self.pnl})>"


# ==================== P&L SNAPSHOTS ====================

class PnLSnapshot(Base):
    """Periodic P&L snapshots for charting and analysis"""
    __tablename__ = 'pnl_snapshots'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Snapshot Details
    snapshot_type = Column(String(20), nullable=False, index=True)  # INTRADAY, DAILY, WEEKLY, MONTHLY
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # P&L Data
    realized_pnl = Column(Numeric(12, 2), default=0)
    unrealized_pnl = Column(Numeric(12, 2), default=0)
    total_pnl = Column(Numeric(12, 2), default=0)
    
    # Cumulative
    cumulative_pnl = Column(Numeric(12, 2), default=0)
    
    # Trade Count
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    
    # Capital
    capital = Column(Numeric(12, 2))
    equity = Column(Numeric(12, 2))
    
    # Relationships
    user = relationship("User", back_populates="pnl_snapshots")
    
    __table_args__ = (
        Index('idx_pnl_user_time', 'user_id', 'snapshot_type', 'timestamp'),
        UniqueConstraint('user_id', 'snapshot_type', 'timestamp', name='uq_pnl_snapshot'),
    )
    
    def __repr__(self):
        return f"<PnLSnapshot(user_id={self.user_id}, type={self.snapshot_type}, pnl={self.total_pnl})>"


# ==================== MARKET EVENTS ====================

class MarketHoliday(Base):
    """Market holidays and trading calendar"""
    __tablename__ = 'market_holidays'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), unique=True, nullable=False, index=True)
    holiday_name = Column(String(100), nullable=False)
    market = Column(String(20), default='NSE')  # NSE, BSE
    description = Column(Text)
    is_trading_day = Column(Boolean, default=False)  # For special trading sessions
    
    def __repr__(self):
        return f"<MarketHoliday(date={self.date}, name={self.holiday_name})>"


class MarketEvent(Base):
    """Important market events and announcements"""
    __tablename__ = 'market_events'
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # EXPIRY, RBI_POLICY, EARNINGS, RESULT
    title = Column(String(200), nullable=False)
    description = Column(Text)
    event_time = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Impact
    impact_level = Column(String(20))  # LOW, MEDIUM, HIGH
    affected_symbols = Column(JSON)  # List of affected indices/symbols
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_event_time_type', 'event_time', 'event_type'),
    )
    
    def __repr__(self):
        return f"<MarketEvent(id={self.id}, type={self.event_type}, title={self.title})>"


# ==================== KILL SWITCH ====================

class KillSwitch(Base):
    """Emergency kill switch for closing positions"""
    __tablename__ = "kill_switch"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), index=True)
    
    # Close Configuration
    close_type = Column(SQLEnum(CloseTypeEnum), nullable=False, index=True)
    close_for = Column(SQLEnum(CloseForEnum), nullable=False, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Execution Details
    reason = Column(Text)
    positions_closed = Column(Integer, default=0)
    orders_cancelled = Column(Integer, default=0)
    
    # Timestamps
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True))
    deactivated_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User")

    __table_args__ = (
        Index('idx_killswitch_active', 'is_active', 'close_type', 'close_for'),
        Index('idx_killswitch_user', 'user_id', 'triggered_at'),
    )
    
    def __repr__(self):
        return f"<KillSwitch(id={self.id}, type={self.close_type}, for={self.close_for}, active={self.is_active})>"


# ==================== SYSTEM SETTINGS ====================

class SystemSettings(Base):
    """Global system settings and configuration"""
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text)
    data_type = Column(String(20))  # STRING, INTEGER, FLOAT, BOOLEAN, JSON
    category = Column(String(50), index=True)  # TRADING, RISK, SYSTEM, NOTIFICATION
    description = Column(Text)
    is_encrypted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SystemSettings(key={self.key}, category={self.category})>"


class SymbolMaster(Base):
    """Master table for all tradable symbols"""
    __tablename__ = 'symbol_master'
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Core Fields
    token = Column(String(50), unique=True, nullable=False, index=True)
    symbol = Column(String(100), unique=True, nullable=False, index=True)
    trading_symbol = Column(String(100), nullable=False, index=True)
    exchange = Column(SQLEnum(ExchangeEnum), nullable=False, index=True)
    
    # Instrument Details
    instrument_type = Column(SQLEnum(InstrumentType), nullable=False, index=True)
    segment = Column(String(20), nullable=False)  # EQ, FO
    
    # For Derivatives
    strike_price = Column(Numeric(10, 2))
    option_type = Column(String(2))  # CE, PE
    expiry_date = Column(DateTime(timezone=True), index=True)
    
    # Trading Parameters
    lot_size = Column(Integer, default=1)
    tick_size = Column(Numeric(10, 6), default=0.05)
    
    # Status Fields
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    
    # Audit Fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_symbol_active', 'is_active', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<SymbolMaster(id={self.id}, symbol={self.symbol}, token={self.token})>"



class SpotTickData(Base):
    """Raw tick data storage"""
    __tablename__ = 'spot_tick_data'
    
    id = Column(BigInteger, primary_key=True, index=True)
    symbol_id = Column(Integer, ForeignKey('symbol_master.id', ondelete='CASCADE'), nullable=False, index=True)
    trade_date = Column(DateTime(timezone=True), nullable=False, index=True)  # ← ADD THIS for partitioning
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # Price Data
    ltp = Column(Numeric(10, 2), nullable=False)

    # Audit Fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(),nullable=True)
    
    # Relationships
    symbol = relationship("SymbolMaster")
   
    # Indexes
    __table_args__ = (
        Index('idx_spot_tick_symbol_time', 'symbol_id', 'timestamp'),
        Index('idx_spot_tick_date', 'trade_date'),
    )
    
    def __repr__(self):
        return f"<SpotTickData(id={self.id}, symbol_id={self.symbol_id}, ltp={self.ltp})>"


class StrikePriceTickData(Base):
    """Strike Price LTP data associated with spot symbols"""
    __tablename__ = 'strike_price_tick_data'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    
    # Foreign Keys
    symbol_master_id = Column(Integer, ForeignKey('symbol_master.id', ondelete='CASCADE'), nullable=False, index=True)    
    # Strike Price
    strike_price = Column(Numeric(10, 2), nullable=False, index=True)
    # LTP
    ltp = Column(Numeric(10, 2), nullable=False)
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    # Indexes
    __table_args__ = (
        Index('idx_strike_price_spot_symbol', 'symbol_master_id', 'strike_price'),
        Index('idx_strike_price_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<StrikePriceTickData(id={self.id}, spot_symbol_id={self.spot_symbol_id}, strike_price={self.strike_price}, ltp={self.ltp})>"


class SignalLog(Base):
    """Trading signal logs for entry and exit signals"""
    __tablename__ = 'signal_logs'
    # Relationships
    orders = relationship("Order", back_populates="signal_log")

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    
    # Signal Details
    token = Column(String(50), nullable=False, index=True)
    signal_type = Column(String(50), nullable=False, index=True)  # BUY_ENTRY, SELL_ENTRY, BUY_EXIT, SELL_EXIT
    unique_id = Column(String(100), nullable=False, index=True)
    strike_price_token = Column(String(50), nullable=False, index=True)
    strategy_code = Column(String(100), nullable=False, index=True)
    signal_category = Column(String(20), nullable=False, index=True)  # ENTRY or EXIT
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_signal_log_unique_id', 'unique_id'),
        Index('idx_signal_log_token_time', 'token', 'timestamp'),
        Index('idx_signal_log_strategy', 'strategy_code', 'timestamp'),
        Index('idx_signal_log_category', 'signal_category', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SignalLog(id={self.id}, signal_type={self.signal_type}, unique_id={self.unique_id})>"

