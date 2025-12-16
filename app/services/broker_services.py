"""
Broker Services Module
Handles authentication and order placement for multiple brokers (Angel One, Dhan)
Optimized for thread-safety, reliability, and maintainability
"""

from dhanhq import dhanhq
from SmartApi import SmartConnect
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import logging
import pyotp
from functools import wraps
import time

# Import broker constants
from app.constants.broker_constants import (
    BrokerType,
    TransactionType,
    OrderType,
    AngelOneExchange,
    AngelOneProductType,
    AngelOneVariety,
    AngelOneDuration,
    AngelOneOrderType,
    DhanExchange,
    DhanProductType,
    DhanOrderType,
    RetryConfig,
    ValidationMessages,
    ANGELONE_REQUIRED_FIELDS,
    DHAN_REQUIRED_FIELDS
)

# Configure logging
logger = logging.getLogger(__name__)


# ==================== DATA MODELS ====================

@dataclass
class BrokerResponse:
    """Standardized broker response format"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    broker: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class AuthResponse:
    """Authentication response with tokens"""
    smart_api_obj: Any
    auth_token: Optional[str] = None
    feed_token: Optional[str] = None
    refresh_token: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None


# ==================== CUSTOM EXCEPTIONS ====================

class BrokerError(Exception):
    """Base exception for broker-related errors"""
    pass


class AuthenticationError(BrokerError):
    """Authentication failed"""
    pass


class OrderPlacementError(BrokerError):
    """Order placement failed"""
    pass


class ValidationError(BrokerError):
    """Input validation failed"""
    pass


# ==================== RETRY DECORATOR ====================

def retry_on_failure(max_attempts: int = None, delay: float = None, backoff: float = None):
    """
    Retry decorator with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts (default from RetryConfig)
        delay: Initial delay between retries in seconds (default from RetryConfig)
        backoff: Multiplier for delay after each attempt (default from RetryConfig)
    """
    # Use defaults from RetryConfig if not provided
    max_attempts = max_attempts or RetryConfig.MAX_ATTEMPTS
    delay = delay or RetryConfig.INITIAL_DELAY
    backoff = backoff or RetryConfig.BACKOFF_MULTIPLIER
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {current_delay:.2f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator


# ==================== VALIDATION FUNCTIONS ====================

def validate_angelone_order_params(order_params: dict) -> Tuple[bool, str]:
    """
    Validate Angel One order parameters
    
    Args:
        order_params: Order parameters dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    for field in ANGELONE_REQUIRED_FIELDS:
        if field not in order_params or order_params[field] is None:
            return False, ValidationMessages.MISSING_FIELD.format(field=field)
    
    # Validate transaction type
    if order_params['transactiontype'] not in ['BUY', 'SELL']:
        return False, ValidationMessages.INVALID_TRANSACTION_TYPE
    
    # Validate quantity
    try:
        qty = int(order_params['quantity'])
        if qty <= 0:
            return False, ValidationMessages.INVALID_QUANTITY
    except (ValueError, TypeError):
        return False, ValidationMessages.INVALID_NUMBER.format(field="Quantity")
    
    # Validate price for LIMIT orders
    if order_params['ordertype'] == 'LIMIT':
        if 'price' not in order_params or order_params['price'] == '0':
            return False, ValidationMessages.PRICE_REQUIRED_FOR_LIMIT
    
    return True, "Valid"


def validate_dhan_order_params(order_params: dict) -> Tuple[bool, str]:
    """
    Validate Dhan order parameters
    
    Args:
        order_params: Order parameters dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    for field in DHAN_REQUIRED_FIELDS:
        if field not in order_params or order_params[field] is None:
            return False, ValidationMessages.MISSING_FIELD.format(field=field)
    
    # Validate transaction type
    if order_params['transaction_type'] not in ['BUY', 'SELL']:
        return False, ValidationMessages.INVALID_TRANSACTION_TYPE
    
    # Validate quantity
    try:
        qty = int(order_params['quantity'])
        if qty <= 0:
            return False, ValidationMessages.INVALID_QUANTITY
    except (ValueError, TypeError):
        return False, ValidationMessages.INVALID_NUMBER.format(field="Quantity")
    
    # Validate price
    try:
        price = float(order_params['price'])
        if price < 0:
            return False, ValidationMessages.INVALID_PRICE
    except (ValueError, TypeError):
        return False, ValidationMessages.INVALID_NUMBER.format(field="Price")
    
    return True, "Valid"



# ==================== ANGEL ONE FUNCTIONS ====================

def angelone_get_auth(api_key: str, username: str, pwd: str, token: str) -> AuthResponse:
    """
    Authenticate with Angel One API using TOTP-based 2FA
    
    Args:
        api_key: Angel One API key
        username: Angel One username/client ID
        pwd: Angel One password/PIN
        token: TOTP secret token for 2FA
        
    Returns:
        AuthResponse object containing SmartConnect instance and tokens
        
    Raises:
        AuthenticationError: If authentication fails
    """
    try:
        logger.info(f"[Angel One] Authenticating user: {username}")
        obj = SmartConnect(api_key=api_key)
        
        # Generate TOTP and authenticate
        totp = pyotp.TOTP(token).now()
        data = obj.generateSession(username, pwd, totp)
        
        # Extract tokens from response
        auth_token = data['data']['jwtToken']
        feed_token = data['data']['feedToken']
        refresh_token = data['data']['refreshToken']
        
        # Get user profile
        profile = obj.getProfile(refresh_token)
        
        logger.info("[Angel One] Authentication successful")
        
        return AuthResponse(
            smart_api_obj=obj,
            auth_token=auth_token,
            feed_token=feed_token,
            refresh_token=refresh_token,
            profile=profile
        )
        
    except Exception as e:
        logger.error(f"[Angel One] Authentication failed: {str(e)}", exc_info=True)
        raise AuthenticationError(f"Angel One authentication failed: {str(e)}") from e


@retry_on_failure(max_attempts=3, delay=1.0, backoff=2.0)
def angelone_place_order(smart_api_obj: SmartConnect, order_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Place an order using Angel One SmartAPI with retry logic
    
    Args:
        smart_api_obj: Authenticated SmartConnect object
        order_details: Order parameters dictionary
        
    Returns:
        Order response from Angel One API
        
    Raises:
        OrderPlacementError: If order placement fails
    """
    try:
        logger.info(f"[Angel One] Placing order: {order_details.get('tradingsymbol')} "
                   f"{order_details.get('transactiontype')} x{order_details.get('quantity')}")
        
        order_response = smart_api_obj.placeOrder(order_details)
        
        if order_response:
            logger.info(f"[Angel One] Order response: {json.dumps(order_response, indent=2)}")
            return order_response
        else:
            logger.warning("[Angel One] Received empty response from placeOrder API")
            raise OrderPlacementError("Empty response from Angel One API")
            
    except Exception as e:
        logger.error(f"[Angel One] Order placement failed: {str(e)}", exc_info=True)
        raise OrderPlacementError(f"Angel One order placement failed: {str(e)}") from e


def place_angelone_order_standalone(
    api_key: str,
    username: str,
    pwd: str,
    token: str,
    order_params: dict
) -> BrokerResponse:
    """
    Standalone function to place an order in Angel One account.
    Handles authentication and order placement in a single call.
    
    Args:
        api_key (str): Angel One API key
        username (str): Angel One username/client ID
        pwd (str): Angel One password/PIN
        token (str): TOTP token for 2FA authentication
        order_params (dict): Order details with following keys:
            - variety (str): "NORMAL", "STOPLOSS", "AMO"
            - tradingsymbol (str): Trading symbol (e.g., "SBIN-EQ", "RELIANCE-EQ")
            - symboltoken (str): Symbol token from Angel One
            - transactiontype (str): "BUY" or "SELL"
            - exchange (str): "NSE", "BSE", "NFO", "MCX", etc.
            - ordertype (str): "MARKET", "LIMIT", "STOPLOSS_LIMIT", "STOPLOSS_MARKET"
            - producttype (str): "DELIVERY", "INTRADAY", "CARRYFORWARD"
            - duration (str): "DAY" or "IOC"
            - price (str): Limit price (use "0" for MARKET orders)
            - squareoff (str): Square off value (use "0" if not applicable)
            - stoploss (str): Stop loss value (use "0" if not applicable)
            - quantity (str): Number of shares/lots
    
    Returns:
        BrokerResponse: Standardized response object
    
    Example:
        >>> result = place_angelone_order_standalone(
        ...     api_key="YOUR_API_KEY",
        ...     username="YOUR_CLIENT_ID",
        ...     pwd="YOUR_PIN",
        ...     token="YOUR_TOTP_SECRET",
        ...     order_params={
        ...         "variety": "NORMAL",
        ...         "tradingsymbol": "SBIN-EQ",
        ...         "symboltoken": "3045",
        ...         "transactiontype": "BUY",
        ...         "exchange": "NSE",
        ...         "ordertype": "MARKET",
        ...         "producttype": "INTRADAY",
        ...         "duration": "DAY",
        ...         "price": "0",
        ...         "squareoff": "0",
        ...         "stoploss": "0",
        ...         "quantity": "10"
        ...     }
        ... )
        >>> print(result.to_dict())
    """
    try:
        # Step 1: Validate order parameters
        is_valid, error_msg = validate_angelone_order_params(order_params)
        if not is_valid:
            logger.error(f"[Angel One] Validation failed: {error_msg}")
            return BrokerResponse(
                success=False,
                message=f"Validation error: {error_msg}",
                broker=BrokerType.ANGEL_ONE.value
            )
        
        # Step 2: Authenticate with Angel One
        logger.info(f"[Angel One] Authenticating user: {username}")
        auth_response = angelone_get_auth(api_key, username, pwd, token)
        
        # Step 3: Place the order
        logger.info(f"[Angel One] Placing {order_params.get('transactiontype')} order "
                   f"for {order_params.get('tradingsymbol')}")
        result = angelone_place_order(
            smart_api_obj=auth_response.smart_api_obj,
            order_details=order_params
        )
        
        # Step 4: Process response
        if result and result.get('status'):
            logger.info(f"[Angel One] ✅ Order placed successfully: Order ID {result.get('data', {}).get('orderid')}")
            return BrokerResponse(
                success=True,
                message="Order placed successfully",
                data=result,
                broker=BrokerType.ANGEL_ONE.value
            )
        else:
            logger.error(f"[Angel One] ❌ Order failed: {result}")
            return BrokerResponse(
                success=False,
                message=result.get('message', 'Order placement failed'),
                data=result,
                broker=BrokerType.ANGEL_ONE.value
            )
    
    except ValidationError as e:
        logger.error(f"[Angel One] Validation error: {str(e)}")
        return BrokerResponse(
            success=False,
            message=f"Validation error: {str(e)}",
            broker=BrokerType.ANGEL_ONE.value
        )
    
    except AuthenticationError as e:
        logger.error(f"[Angel One] Authentication error: {str(e)}")
        return BrokerResponse(
            success=False,
            message=f"Authentication failed: {str(e)}",
            broker=BrokerType.ANGEL_ONE.value
        )
    
    except OrderPlacementError as e:
        logger.error(f"[Angel One] Order placement error: {str(e)}")
        return BrokerResponse(
            success=False,
            message=f"Order placement failed: {str(e)}",
            broker=BrokerType.ANGEL_ONE.value
        )
    
    except Exception as e:
        logger.error(f"[Angel One] Unexpected error: {str(e)}", exc_info=True)
        return BrokerResponse(
            success=False,
            message=f"Unexpected error: {str(e)}",
            broker=BrokerType.ANGEL_ONE.value
        )


# ==================== DHAN FUNCTIONS ====================

@retry_on_failure(max_attempts=3, delay=1.0, backoff=2.0)
def dhan_place_order(dhan_client: dhanhq, order_params: dict) -> dict:
    """
    Place order using Dhan API with retry logic
    
    Args:
        dhan_client: Authenticated Dhan client
        order_params: Order parameters
        
    Returns:
        Order response from Dhan API
        
    Raises:
        OrderPlacementError: If order placement fails
    """
    try:
        logger.info(f"[Dhan] Placing order: Security {order_params.get('security_id')} "
                   f"{order_params.get('transaction_type')} x{order_params.get('quantity')}")
        
        result = dhan_client.place_order(
            security_id=order_params['security_id'],
            exchange_segment=order_params['exchange_segment'],
            transaction_type=order_params['transaction_type'],
            order_type=order_params['order_type'],
            product_type=order_params['product_type'],
            quantity=order_params['quantity'],
            price=order_params['price']
        )
        
        logger.info(f"[Dhan] Order response: {json.dumps(result, indent=2)}")
        return result
        
    except Exception as e:
        logger.error(f"[Dhan] Order placement failed: {str(e)}", exc_info=True)
        raise OrderPlacementError(f"Dhan order placement failed: {str(e)}") from e


def place_dhan_order_standalone(
    client_id: str,
    access_token: str,
    order_params: dict
) -> BrokerResponse:
    """
    Standalone function to place an order in Dhan account.
    Handles authentication and order placement in a single call.
    
    Args:
        client_id (str): Dhan client ID
        access_token (str): Dhan access token
        order_params (dict): Order details with following keys:
            - security_id (str): Dhan security ID (e.g., "1333" for SBIN)
            - exchange_segment (str): "NSE_EQ", "NSE_FNO", "BSE_EQ", "MCX_COMM", 
                                     "BSE_FNO", "NSE_CURRENCY"
            - transaction_type (str): "BUY" or "SELL"
            - order_type (str): "MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_MARKET"
            - product_type (str): 
                * "CNC" - Cash and Carry (Delivery)
                * "INTRA" - Intraday
                * "MARGIN" - Margin
                * "MTF" - Margin Trading Facility
                * "CO" - Cover Order
                * "BO" - Bracket Order
            - quantity (int): Number of shares/lots
            - price (float): Order price (use 0 for MARKET orders)
    
    Returns:
        BrokerResponse: Standardized response object
    
    Example:
        >>> result = place_dhan_order_standalone(
        ...     client_id="YOUR_CLIENT_ID",
        ...     access_token="YOUR_ACCESS_TOKEN",
        ...     order_params={
        ...         "security_id": "1333",
        ...         "exchange_segment": "NSE_EQ",
        ...         "transaction_type": "BUY",
        ...         "order_type": "LIMIT",
        ...         "product_type": "CNC",
        ...         "quantity": 10,
        ...         "price": 500.50
        ...     }
        ... )
        >>> print(result.to_dict())
    
    Note:
        - For MARKET orders, set price to 0
        - Security IDs available from Dhan's security master file
        - Access token can be generated from Dhan's trading platform
    """
    try:
        # Step 1: Validate order parameters
        is_valid, error_msg = validate_dhan_order_params(order_params)
        if not is_valid:
            logger.error(f"[Dhan] Validation failed: {error_msg}")
            return BrokerResponse(
                success=False,
                message=f"Validation error: {error_msg}",
                broker=BrokerType.DHAN.value
            )
        
        # Step 2: Initialize Dhan client
        logger.info(f"[Dhan] Initializing client: {client_id}")
        dhan_client = dhanhq(client_id=client_id, access_token=access_token)
        
        # Step 3: Place the order
        logger.info(f"[Dhan] Placing {order_params.get('transaction_type')} order "
                   f"for security {order_params.get('security_id')}")
        result = dhan_place_order(dhan_client, order_params)
        
        # Step 4: Process response (Dhan uses 'status': 'success'/'failure')
        if result and result.get('status') == 'success':
            logger.info(f"[Dhan] ✅ Order placed successfully: Order ID {result.get('data', {}).get('orderId')}")
            return BrokerResponse(
                success=True,
                message="Order placed successfully",
                data=result,
                broker=BrokerType.DHAN.value
            )
        else:
            logger.error(f"[Dhan] ❌ Order failed: {result}")
            return BrokerResponse(
                success=False,
                message=result.get('remarks', 'Order placement failed'),
                data=result,
                broker=BrokerType.DHAN.value
            )
    
    except ValidationError as e:
        logger.error(f"[Dhan] Validation error: {str(e)}")
        return BrokerResponse(
            success=False,
            message=f"Validation error: {str(e)}",
            broker=BrokerType.DHAN.value
        )
    
    except OrderPlacementError as e:
        logger.error(f"[Dhan] Order placement error: {str(e)}")
        return BrokerResponse(
            success=False,
            message=f"Order placement failed: {str(e)}",
            broker=BrokerType.DHAN.value
        )
    
    except Exception as e:
        logger.error(f"[Dhan] Unexpected error: {str(e)}", exc_info=True)
        return BrokerResponse(
            success=False,
            message=f"Unexpected error: {str(e)}",
            broker=BrokerType.DHAN.value
        )