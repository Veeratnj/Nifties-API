"""
Nifties API - Main application entry point
Trading Platform API for Options Trading
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.models import Base
from app.db.db import engine
from app.middleware.middleware import TimerMiddleware, LoggingMiddleware, AuthMiddleware, ErrorHandlingMiddleware
from app.constants.const import API_TITLE, API_DESCRIPTION, API_VERSION, CORS_ORIGINS

# Import all routers
from app.controllers import (
    health_controller,
    auth_controller,
    market_controller,
    trade_controller,
    order_controller,
    strategy_controller,
    user_controller,
    analytics_controller,
    nifties_opt_controller,
    log_controller,
    alert_controller,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

@app.get("/health")
def health_check():
    return {"status": "ok","version": API_VERSION}

# Add middleware in order (innermost to outermost)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(TimerMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_app():
    """Create and configure the FastAPI application"""
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise
    
    # Register all routers
    app.include_router(health_controller.router)
    app.include_router(auth_controller.router)
    app.include_router(market_controller.router)
    app.include_router(trade_controller.router)
    app.include_router(order_controller.router)
    app.include_router(strategy_controller.router)
    app.include_router(user_controller.router)
    app.include_router(analytics_controller.router)
    app.include_router(nifties_opt_controller.router)
    app.include_router(log_controller.router)
    app.include_router(alert_controller.router)
    
    logger.info("All routers registered successfully")
    logger.info(f"API started on version {API_VERSION}")
    
    return app


# Initialize the application
create_app()


# Startup event
@app.on_event("startup")
async def startup_event():
    """Execute on application startup"""
    logger.info("Application startup")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown"""
    logger.info("Application shutdown")
