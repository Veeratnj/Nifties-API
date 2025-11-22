"""
Application constants
"""

import os

# ==================== JWT Configuration ====================
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# ==================== Logging Configuration ====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "[%(asctime)s] - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/app.log"

# ==================== Trade Constants ====================
TRADES_STATUSES = ["ACTIVE", "CLOSED", "PENDING"]

# ==================== Order Constants ====================
ORDER_STATUSES = ["PENDING", "COMPLETED", "CANCELLED", "REJECTED"]
ORDER_TYPES = ["BUY", "SELL"]

# ==================== Strategy Constants ====================
STRATEGY_STATUSES = ["ACTIVE", "INACTIVE", "COMPLETED"]

# ==================== Alert Types ====================
ALERT_TYPES = ["success", "warning", "error", "info"]

# ==================== Log Constants ====================
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]
LOG_CATEGORIES = ["STRATEGY", "TRADE", "ORDER", "SYSTEM", "USER"]

# ==================== Database ====================
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/db/nifties.db")

# ==================== API Configuration ====================
API_VERSION = "0.0.1"
API_TITLE = "Nifties API"
API_DESCRIPTION = "Trading Platform API for Options Trading"

# ==================== CORS ====================
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# ==================== Pagination ====================
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# ==================== Indices ====================
SUPPORTED_INDICES = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]

# ==================== Contract Types ====================
CONTRACT_TYPES = ["CE", "PE"]  # Call Option, Put Option

# ==================== Period Types ====================
PERIOD_TYPES = ["today", "week", "month"]
