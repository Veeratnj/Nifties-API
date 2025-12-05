"""
Controller for Trading Signal APIs
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.schemas.signal_schema import SignalEntryRequest, SignalExitRequest, SignalResponse
from app.services.signal_service import SignalService

router = APIRouter(
    prefix="/db/signals",
    tags=["Trading Signals"]
)


@router.post("/entry", response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def send_entry_signal(
    signal_data: SignalEntryRequest,
    db: Session = Depends(get_db)
):
    """
    Send trading entry signal to the API.
    This is a POST API with no authentication required.
    
    **Request Body Example:**
    ```json
    {
        "token": "23",
        "signal": "BUY_ENTRY",
        "unique_id": "unique_123",
        "strike_price_token": "45678",
        "strategy_code": "STRATEGY_001"
    }
    ```
    
    **Response:**
    - 201: Entry signal sent successfully
    - 400: Invalid data
    - 500: Server error
    """
    try:
        # Process entry signal
        result = SignalService.process_entry_signal(db, signal_data)
        
        return SignalResponse(
            success=True,
            message="Entry signal sent successfully",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send entry signal: {str(e)}"
        )


@router.post("/exit", response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def send_exit_signal(
    signal_data: SignalExitRequest,
    db: Session = Depends(get_db)
):
    """
    Send trading exit signal to the API.
    This is a POST API with no authentication required.
    
    **Request Body Example:**
    ```json
    {
        "token": "23",
        "signal": "BUY_EXIT",
        "unique_id": "unique_123",
        "strike_price_token": "45678",
        "strategy_code": "STRATEGY_001"
    }
    ```
    
    **Response:**
    - 201: Exit signal sent successfully
    - 400: Invalid data
    - 500: Server error
    """
    try:
        # Process exit signal
        result = SignalService.process_exit_signal(db, signal_data)
        
        return SignalResponse(
            success=True,
            message="Exit signal sent successfully",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send exit signal: {str(e)}"
        )
