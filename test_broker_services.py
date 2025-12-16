"""
Test file for broker_services.py
Demonstrates usage of refactored broker services
"""

from app.services.broker_services import (
    place_angelone_order_standalone,
    place_dhan_order_standalone,
    BrokerResponse,
    validate_angelone_order_params,
    validate_dhan_order_params
)
from app.constants.broker_constants import (
    BrokerType,
    TransactionType,
    AngelOneExchange,
    DhanExchange
)


def test_angelone_validation():
    """Test Angel One order parameter validation"""
    print("\n" + "="*60)
    print("Testing Angel One Order Validation")
    print("="*60)
    
    # Valid order
    valid_order = {
        "variety": "NORMAL",
        "tradingsymbol": "SBIN-EQ",
        "symboltoken": "3045",
        "transactiontype": "BUY",
        "exchange": "NSE",
        "ordertype": "MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "0",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": "10"
    }
    
    is_valid, msg = validate_angelone_order_params(valid_order)
    print(f"✅ Valid order: {is_valid} - {msg}")
    
    # Invalid order - missing field
    invalid_order = {
        "variety": "NORMAL",
        "tradingsymbol": "SBIN-EQ",
        # Missing symboltoken
        "transactiontype": "BUY",
    }
    
    is_valid, msg = validate_angelone_order_params(invalid_order)
    print(f"❌ Invalid order (missing field): {is_valid} - {msg}")
    
    # Invalid order - wrong transaction type
    invalid_order2 = valid_order.copy()
    invalid_order2["transactiontype"] = "INVALID"
    
    is_valid, msg = validate_angelone_order_params(invalid_order2)
    print(f"❌ Invalid order (wrong type): {is_valid} - {msg}")


def test_dhan_validation():
    """Test Dhan order parameter validation"""
    print("\n" + "="*60)
    print("Testing Dhan Order Validation")
    print("="*60)
    
    # Valid order
    valid_order = {
        "security_id": "1333",
        "exchange_segment": "NSE_EQ",
        "transaction_type": "BUY",
        "order_type": "LIMIT",
        "product_type": "CNC",
        "quantity": 10,
        "price": 500.50
    }
    
    is_valid, msg = validate_dhan_order_params(valid_order)
    print(f"✅ Valid order: {is_valid} - {msg}")
    
    # Invalid order - negative price
    invalid_order = valid_order.copy()
    invalid_order["price"] = -100
    
    is_valid, msg = validate_dhan_order_params(invalid_order)
    print(f"❌ Invalid order (negative price): {is_valid} - {msg}")
    
    # Invalid order - zero quantity
    invalid_order2 = valid_order.copy()
    invalid_order2["quantity"] = 0
    
    is_valid, msg = validate_dhan_order_params(invalid_order2)
    print(f"❌ Invalid order (zero quantity): {is_valid} - {msg}")


def test_broker_response():
    """Test BrokerResponse model"""
    print("\n" + "="*60)
    print("Testing BrokerResponse Model")
    print("="*60)
    
    # Success response
    success_response = BrokerResponse(
        success=True,
        message="Order placed successfully",
        data={"order_id": "123456"},
        broker="ANGEL_ONE"
    )
    
    print("Success Response:")
    print(success_response.to_dict())
    
    # Failure response
    failure_response = BrokerResponse(
        success=False,
        message="Validation error: Missing required field",
        broker="DHAN"
    )
    
    print("\nFailure Response:")
    print(failure_response.to_dict())


def example_angelone_usage():
    """
    Example usage of Angel One order placement
    NOTE: This is just an example. Replace with actual credentials to test.
    """
    print("\n" + "="*60)
    print("Example: Angel One Order Placement")
    print("="*60)
    
    # Example order parameters
    order_params = {
        "variety": "NORMAL",
        "tradingsymbol": "SBIN-EQ",
        "symboltoken": "3045",
        "transactiontype": "BUY",
        "exchange": "NSE",
        "ordertype": "MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "0",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": "1"
    }
    
    print("Order Parameters:")
    print(order_params)
    print("\nTo place actual order, uncomment and use:")
    print("""
    result = place_angelone_order_standalone(
        api_key="YOUR_API_KEY",
        username="YOUR_CLIENT_ID",
        pwd="YOUR_PIN",
        token="YOUR_TOTP_SECRET",
        order_params=order_params
    )
    
    if result.success:
        print(f"✅ Order placed: {result.data}")
    else:
        print(f"❌ Order failed: {result.message}")
    """)


def example_dhan_usage():
    """
    Example usage of Dhan order placement
    NOTE: This is just an example. Replace with actual credentials to test.
    """
    print("\n" + "="*60)
    print("Example: Dhan Order Placement")
    print("="*60)
    
    # Example order parameters
    order_params = {
        "security_id": "1333",
        "exchange_segment": "NSE_EQ",
        "transaction_type": "BUY",
        "order_type": "MARKET",
        "product_type": "INTRA",
        "quantity": 1,
        "price": 0
    }
    
    print("Order Parameters:")
    print(order_params)
    print("\nTo place actual order, uncomment and use:")
    print("""
    result = place_dhan_order_standalone(
        client_id="YOUR_CLIENT_ID",
        access_token="YOUR_ACCESS_TOKEN",
        order_params=order_params
    )
    
    if result.success:
        print(f"✅ Order placed: {result.data}")
    else:
        print(f"❌ Order failed: {result.message}")
    """)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("BROKER SERVICES - REFACTORED VERSION TESTS")
    print("="*60)
    
    # Run validation tests
    test_angelone_validation()
    test_dhan_validation()
    
    # Test response model
    test_broker_response()
    
    # Show usage examples
    example_angelone_usage()
    example_dhan_usage()
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)
