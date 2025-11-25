"""
Enhanced middleware for logging, timing, and authentication
"""

import time
import logging
import json
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from fastapi import Request as FastAPIRequest
import os

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class TimerMiddleware(BaseHTTPMiddleware):
    """Middleware to track request processing time"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Error in request: {str(e)}, processed in {process_time:.4f}s")
            raise


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip logging for health checks
        if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        start_time = time.time()
        request_id = request.headers.get("X-Request-ID", str(datetime.utcnow().timestamp()))
        
        # Log incoming request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"[{request_id}] Response {response.status_code} - "
                f"Processing time: {process_time:.4f}s"
            )
            
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] Error: {str(e)} - "
                f"Processing time: {process_time:.4f}s"
            )
            raise


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for authentication logging"""
    
    # Public endpoints that don't require authentication
    PUBLIC_ENDPOINTS = ["/", "/health", "/api/auth/login", "/api/auth/register", "/docs", "/openapi.json", "/redoc", "/db"]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Check if endpoint is public
        if any(request.url.path.startswith(endpoint) for endpoint in self.PUBLIC_ENDPOINTS):
            return await call_next(request)
        
        # Get token from header
        auth_header = request.headers.get("authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"Unauthorized access attempt to {request.url.path}")
        else:
            token = auth_header.split(" ")[1]
            logger.debug(f"Authenticated request to {request.url.path}")
        
        return await call_next(request)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for consistent error handling"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            raise
