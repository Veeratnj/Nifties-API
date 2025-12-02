"""
Service layer for Tick Data operations
"""

from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from app.models.models import SpotTickData, StrikePriceTickData, HistoricalData, TimeFrame, SymbolMaster
from app.schemas.schema import TickDataInsert, StrikePriceLTPInsert, OHLCDataInsert


class TickLTPService:
    """Service class for tick LTP operations (for API endpoints)"""
    
    @staticmethod
    def insert_spot_ltp(db: Session, tick_data: TickDataInsert) -> SpotTickData:
        """
        Insert spot symbol LTP data using token
        
        Args:
            db: Database session
            tick_data: Tick data to insert (with token)
            
        Returns:
            Created SpotTickData object
            
        Raises:
            Exception: If token not found or database operation fails
        """
        try:
            # Look up symbol_id from token
            symbol = db.query(SymbolMaster).filter(
                SymbolMaster.token == tick_data.token,
                SymbolMaster.is_active == True,
                SymbolMaster.is_deleted == False
            ).first()
            print('symbol:::', symbol)
            if not symbol:
                raise Exception(f"Symbol with token '{tick_data.token}' not found or inactive")
            
            # Extract trade_date from timestamp (date part only)
            trade_date = tick_data.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Create tick data entry
            db_tick = SpotTickData(
                symbol_id=symbol.id,
                timestamp=tick_data.timestamp,
                ltp=tick_data.ltp,
                trade_date=tick_data.timestamp,
                # volume=tick_data.volume,
                # oi=tick_data.oi,
                # bid_price=tick_data.bid_price,
                # bid_qty=tick_data.bid_qty,
                # ask_price=tick_data.ask_price,
                # ask_qty=tick_data.ask_qty
            )
            
            db.add(db_tick)
            db.commit()
            db.refresh(db_tick)
            
            return db_tick
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Error inserting spot LTP data: {str(e)}")

    
    @staticmethod
    def insert_strike_ltp(db: Session, strike_ltp_data: StrikePriceLTPInsert) -> StrikePriceTickData:
        """
        Insert strike price LTP data
        
        Args:
            db: Database session
            strike_ltp_data: Strike price LTP data to insert
            
        Returns:
            Created StrikePriceTickData object
            
        Raises:
            Exception: If database operation fails
        """
        try:
            print('check 0.1')
            symbol_master_id = db.query(SymbolMaster).filter(
                    SymbolMaster.token == strike_ltp_data.strike_price_token,
                    SymbolMaster.instrument_type=='OPT_INDEX',
                    SymbolMaster.is_active == True,
                    SymbolMaster.is_deleted == False
                ).first()

            print('check 1',symbol_master_id.id)
            db_strike_ltp = StrikePriceTickData(
                symbol_master_id=symbol_master_id.id,
                ltp=strike_ltp_data.ltp,
                created_at=strike_ltp_data.timestamp,
                strike_price=strike_ltp_data.strike_price,
            )
            
            db.add(db_strike_ltp)
            db.commit()
            db.refresh(db_strike_ltp)
            
            return db_strike_ltp
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Error inserting strike price LTP data: {str(e)}")

    
    @staticmethod
    def format_spot_ltp_response(db_tick: SpotTickData) -> Dict[str, Any]:
        """
        Format spot LTP data for API response
        
        Args:
            db_tick: SpotTickData object
            
        Returns:
            Formatted dictionary for API response
        """
        return {
            "id": db_tick.id,
            "symbol_id": db_tick.symbol_id,
            "ltp": float(db_tick.ltp),
            "timestamp": db_tick.timestamp.isoformat()
        }

    
    @staticmethod
    def format_strike_ltp_response(db_strike_ltp: StrikePriceTickData) -> Dict[str, Any]:
        """
        Format strike price LTP data for API response
        
        Args:
            db_strike_ltp: StrikePriceTickData object
            
        Returns:
            Formatted dictionary for API response
        """
        return None

    
    @staticmethod
    def insert_ohlc_data(db: Session, ohlc_data: OHLCDataInsert) -> HistoricalData:
        """
        Insert OHLC historical data
        
        Args:
            db: Database session
            ohlc_data: OHLC data to insert
            
        Returns:
            Created HistoricalData object
            
        Raises:
            Exception: If database operation fails
        """
        try:
            print(f"DEBUG: Received OHLC data: symbol={ohlc_data.symbol}, timeframe={ohlc_data.timeframe}")
            
            # Convert timeframe string to enum
            timeframe_enum = TimeFrame(ohlc_data.timeframe)
            print(f"DEBUG: Converted to enum: {timeframe_enum}")
            
            # Create historical data entry
            print(f"DEBUG: Creating HistoricalData object :: {ohlc_data}")
            from datetime import timezone, timedelta
            IST = timezone(timedelta(hours=5, minutes=30))
            db_ohlc = HistoricalData(
                symbol=ohlc_data.symbol,
                timeframe=timeframe_enum,
                timestamp=ohlc_data.timestamp.astimezone(IST),
                open=ohlc_data.open,
                high=ohlc_data.high,
                low=ohlc_data.low,
                close=ohlc_data.close,
                volume=ohlc_data.volume
            )
            print(f"DEBUG: Created HistoricalData object")
            
            db.add(db_ohlc)
            print(f"DEBUG: Added to session")
            db.commit()
            print(f"DEBUG: Committed to database")
            db.refresh(db_ohlc)
            print(f"DEBUG: Refreshed object, ID: {db_ohlc.id}")
            
            return db_ohlc
            
        except ValueError as e:
            db.rollback()
            import traceback
            error_detail = traceback.format_exc()
            raise Exception(f"Invalid timeframe value '{ohlc_data.timeframe}'. Must be one of: {', '.join([tf.value for tf in TimeFrame])}. Error: {str(e)}")
        except Exception as e:
            db.rollback()
            import traceback
            error_detail = traceback.format_exc()
            raise Exception(f"Error inserting OHLC data: {str(e)}. Traceback: {error_detail}")

    
    @staticmethod
    def format_ohlc_response(db_ohlc: HistoricalData) -> Dict[str, Any]:
        """
        Format OHLC data for API response
        
        Args:
            db_ohlc: HistoricalData object
            
        Returns:
            Formatted dictionary for API response
        """
        return {
            "id": db_ohlc.id,
            "symbol": db_ohlc.symbol,
            "timeframe": db_ohlc.timeframe.value if db_ohlc.timeframe else None,
            "timestamp": db_ohlc.timestamp.isoformat() if db_ohlc.timestamp else None,
            "open": float(db_ohlc.open),
            "high": float(db_ohlc.high),
            "low": float(db_ohlc.low),
            "close": float(db_ohlc.close),
            "volume": db_ohlc.volume
        }

