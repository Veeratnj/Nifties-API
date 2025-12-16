"""
Broker Constants and Enums
Contains all broker-related constants, enums, and configuration values
"""

from enum import Enum


# ==================== BROKER TYPES ====================

class BrokerType(str, Enum):
    """Supported broker types"""
    ANGEL_ONE = "ANGEL_ONE"
    DHAN = "DHAN"


# ==================== COMMON TRADING ENUMS ====================

class TransactionType(str, Enum):
    """Order transaction types"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order types"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_MARKET = "STOP_LOSS_MARKET"


# ==================== ANGEL ONE CONSTANTS ====================

class AngelOneExchange(str, Enum):
    """Angel One exchange types"""
    NSE = "NSE"
    BSE = "BSE"
    NFO = "NFO"
    MCX = "MCX"
    BFO = "BFO"
    CDS = "CDS"


class AngelOneProductType(str, Enum):
    """Angel One product types"""
    DELIVERY = "DELIVERY"
    INTRADAY = "INTRADAY"
    CARRYFORWARD = "CARRYFORWARD"


class AngelOneVariety(str, Enum):
    """Angel One order varieties"""
    NORMAL = "NORMAL"
    STOPLOSS = "STOPLOSS"
    AMO = "AMO"


class AngelOneDuration(str, Enum):
    """Angel One order duration"""
    DAY = "DAY"
    IOC = "IOC"


class AngelOneOrderType(str, Enum):
    """Angel One specific order types"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOPLOSS_LIMIT = "STOPLOSS_LIMIT"
    STOPLOSS_MARKET = "STOPLOSS_MARKET"


# ==================== DHAN CONSTANTS ====================

class DhanExchange(str, Enum):
    """Dhan exchange segments"""
    NSE_EQ = "NSE_EQ"
    NSE_FNO = "NSE_FNO"
    BSE_EQ = "BSE_EQ"
    BSE_FNO = "BSE_FNO"
    MCX_COMM = "MCX_COMM"
    NSE_CURRENCY = "NSE_CURRENCY"


class DhanProductType(str, Enum):
    """Dhan product types"""
    CNC = "CNC"          # Cash and Carry (Delivery)
    INTRA = "INTRA"      # Intraday
    MARGIN = "MARGIN"    # Margin
    MTF = "MTF"          # Margin Trading Facility
    CO = "CO"            # Cover Order
    BO = "BO"            # Bracket Order


class DhanOrderType(str, Enum):
    """Dhan order types"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_MARKET = "STOP_LOSS_MARKET"


# ==================== RETRY CONFIGURATION ====================

class RetryConfig:
    """Retry configuration for broker API calls"""
    MAX_ATTEMPTS = 3
    INITIAL_DELAY = 1.0  # seconds
    BACKOFF_MULTIPLIER = 2.0


# ==================== VALIDATION CONSTANTS ====================

class ValidationMessages:
    """Standard validation error messages"""
    MISSING_FIELD = "Missing required field: {field}"
    INVALID_TRANSACTION_TYPE = "Invalid transaction type. Must be 'BUY' or 'SELL'"
    INVALID_QUANTITY = "Quantity must be greater than 0"
    INVALID_PRICE = "Price cannot be negative"
    PRICE_REQUIRED_FOR_LIMIT = "Price is required for LIMIT orders"
    INVALID_NUMBER = "{field} must be a valid number"


# ==================== ANGEL ONE REQUIRED FIELDS ====================

ANGELONE_REQUIRED_FIELDS = [
    'variety',
    'tradingsymbol',
    'symboltoken',
    'transactiontype',
    'exchange',
    'ordertype',
    'producttype',
    'duration',
    'quantity'
]


# ==================== DHAN REQUIRED FIELDS ====================

DHAN_REQUIRED_FIELDS = [
    'security_id',
    'exchange_segment',
    'transaction_type',
    'order_type',
    'product_type',
    'quantity',
    'price'
]
