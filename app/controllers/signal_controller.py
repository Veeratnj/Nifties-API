"""
Controller for Trading Signal APIs
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
import logging

from sqlalchemy.orm import Session
from typing import Optional
from fastapi import BackgroundTasks
from fastapi import Request
from app.models.models import SignalLog, AdminDhanCreds , StrikePriceTickData
from app.db.db import get_db
from app.schemas.signal_schema import SignalEntryRequest, SignalExitRequest, SignalResponse, LTPInsertRequest
from app.services.signal_service import SignalService
from app.services.enhanced_signal_services import EnhancedSignalService
import asyncio
router = APIRouter(
    prefix="/db/signals",
    tags=["Trading Signals"]
)

logger = logging.getLogger(__name__)



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


# ============================================================================
# V2 ENDPOINTS - Enhanced Multi-Trader Signal Processing
# ============================================================================

@router.post("/v2/entry", response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def send_entry_signal_v2(
    signal_data: SignalEntryRequest,
    db: Session = Depends(get_db)
):
    """
    **V2 Enhanced Entry Signal** - Broadcasts entry signal to all active traders.
    
    This endpoint uses the EnhancedSignalService to process entry signals
    for multiple traders simultaneously. Each active trader will receive:
    - A new Position record
    - An entry Order record
    - Automatic risk management (5% SL, 10% Target)
    
    **Request Body Example:**
    ```json
    {
        "token": "23",
        "signal": "BUY_ENTRY",
        "unique_id": "unique_123",
        "strategy_code": "STRATEGY_001"
    }
    ```
    
    **Response Example:**
    ```json
    {
        "success": true,
        "message": "Entry signal processed for all traders",
        "data": {
            "signal_log_id": 1,
            "signal_type": "BUY_ENTRY",
            "unique_id": "unique_123",
            "total_traders": 5,
            "successful_entries": 5,
            "failed_entries": 0,
            "trader_results": [
                {
                    "user_id": 1,
                    "username": "trader1",
                    "position_id": 101,
                    "order_id": "1_unique_123_1234567890.123",
                    "qty": 1,
                    "entry_price": 100.0,
                    "status": "SUCCESS"
                }
            ]
        }
    }
    ```
    
    **Response:**
    - 201: Entry signal processed successfully for all traders
    - 500: Server error
    """
    try:
        # Process entry signal using enhanced service
        result = EnhancedSignalService.process_entry_signal(db, signal_data)
        
        return SignalResponse(
            success=True,
            message=f"Entry signal processed for {result['total_traders']} traders",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process entry signal: {str(e)}"
        )


@router.post("/v2/exit", response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def send_exit_signal_v2(
    signal_data: SignalExitRequest,
    db: Session = Depends(get_db)
):
    """
    **V2 Enhanced Exit Signal** - Closes all matching positions for all traders.
    
    This endpoint uses the EnhancedSignalService to process exit signals
    for all open positions matching the signal's unique_id or symbol.
    For each position, it will:
    - Create an exit Order record
    - Close the Position
    - Calculate P&L (profit/loss)
    - Create a Trade record
    
    **Request Body Example:**
    ```json
    {
        "token": "23",
        "signal": "BUY_EXIT",
        "unique_id": "unique_123",
        "strategy_code": "STRATEGY_001"
    }
    ```
    
    **Response Example:**
    ```json
    {
        "success": true,
        "message": "Exit signal processed for 5 positions",
        "data": {
            "signal_log_id": 2,
            "signal_type": "BUY_EXIT",
            "unique_id": "unique_123",
            "total_positions": 5,
            "successful_exits": 5,
            "failed_exits": 0,
            "trader_results": [
                {
                    "user_id": 1,
                    "position_id": 101,
                    "order_id": "1_EXIT_unique_123_1234567890.123",
                    "qty": 1,
                    "entry_price": 100.0,
                    "exit_price": 110.0,
                    "pnl": 10.0,
                    "pnl_percent": 10.0,
                    "status": "SUCCESS"
                }
            ]
        }
    }
    ```
    
    **Response:**
    - 201: Exit signal processed successfully
    - 500: Server error
    """
    try:
        # Process exit signal using enhanced service
        result = EnhancedSignalService.process_exit_signal(db, signal_data)
        
        return SignalResponse(
            success=True,
            message=f"Exit signal processed for {result['total_positions']} positions",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process exit signal: {str(e)}"
        )


@router.get("/v2/active-positions", response_model=SignalResponse, status_code=status.HTTP_200_OK)
async def get_active_positions(
    strategy_code: str = Query(..., description="Strategy code to filter positions"),
    user_id: Optional[int] = Query(None, description="Optional user ID to filter positions"),
    db: Session = Depends(get_db)
):
    """
    **V2 Get Active Positions** - Retrieve all active positions for a strategy.
    
    This endpoint retrieves all open positions filtered by strategy code
    and optionally by user ID.
    
    **Query Parameters:**
    - `strategy_code` (required): Strategy code to filter (e.g., "STRATEGY_001")
    - `user_id` (optional): User ID to filter positions for a specific trader
    
    **Response Example:**
    ```json
    {
        "success": true,
        "message": "Retrieved 5 active positions",
        "data": [
            {
                "position_id": 101,
                "user_id": 1,
                "symbol": "NIFTY23DEC23500CE",
                "underlying": "NIFTY",
                "qty": 1,
                "entry_price": 100.0,
                "unrealized_pnl": 10.0,
                "entry_time": "2025-12-09T09:30:00+05:30"
            }
        ]
    }
    ```
    
    **Response:**
    - 200: Active positions retrieved successfully
    - 500: Server error
    """
    try:
        # Get active positions using enhanced service
        positions = EnhancedSignalService.get_active_positions_by_strategy(
            db=db,
            strategy_code=strategy_code,
            user_id=user_id
        )
        
        return SignalResponse(
            success=True,
            message=f"Retrieved {len(positions)} active positions",
            data=positions
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve active positions: {str(e)}"
        )



@router.post("/entry/v3", response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def send_entry_signal_v3(
    signal_data: SignalEntryRequest,
    request: Request,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks=None,
    
):
    try:
        # try:
        #     from app.services.ltp_ws_service import start_ltp_websocket
        #     background_tasks.add_task(
        #         asyncio.to_thread,
        #         start_ltp_websocket,
        #         signal_data.token,   # token from your request
        #         request.app,               # your FastAPI app instance if needed for app.state
        #     )
        #     logger.info(f"LTP WebSocket started for token {signal_data.strike_data.token}")
        #     print('LTP WebSocket started for token',signal_data.strike_data.token)
        # except Exception as e:
        #     print('Exception',e)
        #     logger.error(f"Failed to start LTP WebSocket: {str(e)}")    

        SignalService.process_entry_signal_v3(db=db, signal_data=signal_data,request=request)

        return SignalResponse(
            success=True,
            message="Entry signal v3 processed successfully",
            data={}
        )
    except Exception as e:
        print('Exception',e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process entry signal: {str(e)}"
        )


@router.post("/exit/v3", response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def send_exit_signal_v3(
    signal_data: SignalExitRequest,
    db: Session = Depends(get_db)
):
    try:
        SignalService.process_exit_signal_v3(db=db, signal_data=signal_data)
        return SignalResponse(
            success=True,
            message="Exit signal v3 processed successfully",
            data={}
        )
    except Exception as e:
        print('Exception',e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process exit signal: {str(e)}"
        )


@router.post("/strike-ltp", response_model=SignalResponse, status_code=status.HTTP_200_OK)
async def insert_strike_ltp(
    ltp_data: LTPInsertRequest,
    db: Session = Depends(get_db)
):
    """
    **Manual LTP Insertion** - Persists LTP value in database.
    
    This endpoint allows manual insertion of LTP values into the `strike_price_tick_data` table.
    The system then uses this data for PnL calculations via DB joins.
    """
    try:
        print('ltp_data',ltp_data,'qwe123')
        # 1. Persist to Database
        from app.services.tick_service import TickLTPService
        # from app.schemas.schema import StrikePriceLTPInsert
        import datetime
        from app.models import StrikePriceTickData
        
        # # Prepare data for service
        # db_insert_data = StrikePriceLTPInsert(
        #     token=ltp_data.token,
        #     symbol=ltp_data.symbol,
        #     ltp=ltp_data.ltp,
        #     timestamp=datetime.datetime.now().isoformat()
        # )
        db_insert_data = StrikePriceTickData(
            token=ltp_data.token,
            symbol=ltp_data.symbol,
            ltp=ltp_data.ltp,
            created_at=datetime.datetime.now().isoformat()
        )
        db.add(db_insert_data)
        db.commit()
        # TickLTPService.insert_strike_ltp(db, db_insert_data)

        # logger.info(f"Manual LTP insertion for token {ltp_data.token}: {ltp_data.ltp}")
        
        return SignalResponse(
            success=True,
            message="LTP stored and persisted successfully",
            data={"token": ltp_data.token, "ltp": float(ltp_data.ltp), "symbol": ltp_data.symbol}
        )
        
    except Exception as e:
        # logger.error(f"Failed to insert manual LTP: {str(e)}")
        print('Exception',e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store LTP: {str(e)}"
        )


@router.post("/multiple-strike-price-entry", response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def multiple_strike_price_entry(
    signal_data: list[LTPInsertRequest],
    db: Session = Depends(get_db)
                                    ):
    try:
        for ltp_data in signal_data:
            await insert_strike_ltp(ltp_data=ltp_data, db=db)
        return SignalResponse(
            success=True,
            message="Multiple strike price entry processed successfully",
            data={}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process multiple strike price entry: {str(e)}"
        )


@router.get("/{unique_id}")
async def get_stop_loss_target(unique_id: str, db: Session = Depends(get_db)):
    try:
        signal = db.query(SignalLog).filter(SignalLog.unique_id == unique_id).first()
        if not signal:
            return {
                "stop_loss": None,
                "target": None,
            }
        return {
            "stop_loss": signal.stop_loss,
            "target": signal.target,
                # "description": signal.description
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/get-stop-loss-target/v1/{unique_id}", status_code=status.HTTP_200_OK)
async def get_stop_loss_target(unique_id: str, db: Session = Depends(get_db)):
    try:
        signal = db.query(SignalLog).filter(SignalLog.unique_id == unique_id,SignalLog.signal_category == "ENTRY").first()
        if not signal:
            return {
                "stop_loss": None,
                "target": None,
            }
        return {
            "stop_loss": signal.stop_loss,
            "target": signal.target,
                # "description": signal.description
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.get("/get-admin-dhan-creds/{id}")
def get_admin_dhan_creds(
    id: int,
    db: Session = Depends(get_db)
):
    admin_dhan_creds = (
        db.query(
            AdminDhanCreds.client_id,
            AdminDhanCreds.access_token
        )
        .filter(
            AdminDhanCreds.id == id,
            AdminDhanCreds.is_deleted == False
        )
        .first()
    )

    if not admin_dhan_creds:
        return None

    return {
        "client_id": admin_dhan_creds.client_id,
        "access_token": admin_dhan_creds.access_token
    }

        # 

@router.put("/update-stop-loss-target/v1", status_code=status.HTTP_200_OK)
async def update_stop_loss_target(stop_loss: float=None, target: float=None,unique_id: str=None, db: Session = Depends(get_db)):
    try:
        signal = db.query(SignalLog).filter(SignalLog.unique_id == unique_id,SignalLog.signal_category == "ENTRY").first()
        if not signal:
            return {
                "stop_loss": None,
                "target": None,
            }
        if stop_loss:
            signal.stop_loss = stop_loss
        if target:  
            signal.target = target
        db.commit()
        return {
            "stop_loss": signal.stop_loss,
            "target": signal.target,
                # "description": signal.description
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.get("/get-strike-price-close-trade-signal/{unique_id}")
async def get_strike_price_close_trade_signal(
    unique_id: str, 
    db: Session = Depends(get_db)
):
    try:
        signal = (
            db.query(SignalLog)
            .filter(
                SignalLog.unique_id == unique_id,
                SignalLog.signal_category == "ENTRY"
            )
            .first()
        )

        if not signal:
            return False   # No entry signal found

        # Fetch only LTP value (not a tuple)
        ltp_row = (
            db.query(StrikePriceTickData.ltp)
            .filter(StrikePriceTickData.token == signal.strike_price_token)
            .first()
        )

        if not ltp_row:
            return False   # No live price found

        ltp = ltp_row[0]  # ✅ IMPORTANT FIX

        sl = signal.strike_price_stop_loss
        target = signal.strike_price_target

        if sl is None or target is None:
            return False

        # Close trade if SL hit OR Target hit
        if ltp <= sl or ltp >= target:
            return True

        return False

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
