"""
Enhanced Service layer for Signal operations with multi-trader support
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from decimal import Decimal

from app.schemas.signal_schema import SignalEntryRequest, SignalExitRequest
from app.models.models import (
    SignalLog, User, Position, Order, Trade, SymbolMaster,
    PositionStatus, OrderStatus, OrderType, UserRole
)


class EnhancedSignalService:
    """Enhanced service class for trading signal operations with multi-trader support"""
    
    # Default configurations (can be moved to database settings)
    DEFAULT_QTY = 1
    DEFAULT_PRODUCT_TYPE = "NRML"
    DEFAULT_ORDER_TYPE = "MARKET"
    IST = ZoneInfo("Asia/Kolkata")
    
    @staticmethod
    def _get_active_traders(db: Session, strategy_code: Optional[str] = None) -> List[User]:
        """
        Get all active traders who should receive signals
        
        Args:
            db: Database session
            strategy_code: Optional strategy code filter
            
        Returns:
            List of active User objects
        """
        query = db.query(User).filter(
            User.is_active == True,
            User.role.in_([UserRole.TRADER, UserRole.ADMIN, UserRole.SUPERADMIN]),
            User.kyc_verified == True
        )
        
        # TODO: Add strategy subscription filter if needed
        # if strategy_code:
        #     query = query.join(UserStrategySubscription).filter(
        #         UserStrategySubscription.strategy_code == strategy_code
        #     )
        
        return query.all()
    
    @staticmethod
    def _get_symbol_details(db: Session, token: str) -> Optional[SymbolMaster]:
        """Get symbol details from token"""
        return db.query(SymbolMaster).filter(
            SymbolMaster.token == token,
            SymbolMaster.is_active == True,
            SymbolMaster.is_deleted == False
        ).first()
    
    @staticmethod
    def _get_strike_symbol_details(db: Session, strike_token: str) -> Optional[SymbolMaster]:
        """Get strike price symbol details from token"""
        return db.query(SymbolMaster).filter(
            SymbolMaster.token == strike_token,
            SymbolMaster.is_active == True,
            SymbolMaster.is_deleted == False
        ).first()
    
    @staticmethod
    def _create_position(
        db: Session,
        user_id: int,
        strategy_code: str,
        signal_data: SignalEntryRequest,
        symbol: SymbolMaster,
        strike_symbol: SymbolMaster,
        entry_price: Decimal,
        qty: int
    ) -> Position:
        """Create a new position for a trader"""
        
        position = Position(
            user_id=user_id,
            # strategy_id will be set if Strategy record exists
            symbol=strike_symbol.symbol,
            underlying=symbol.symbol,
            strike_price=int(strike_symbol.strike_price) if strike_symbol.strike_price else 0,
            option_type=strike_symbol.option_type or "CE",
            expiry_date=strike_symbol.expiry_date or datetime.now(EnhancedSignalService.IST) + timedelta(days=7),
            qty=qty,
            avg_entry_price=entry_price,
            status=PositionStatus.OPEN,
            entry_time=datetime.now(EnhancedSignalService.IST),
            # Default risk management (can be customized per user)
            stop_loss=entry_price * Decimal('0.95'),  # 5% stop loss
            target=entry_price * Decimal('1.10'),  # 10% target
            trailing_sl=False,
            margin_used=entry_price * qty  # Simplified margin calculation
        )
        
        return position
    
    @staticmethod
    def _create_order(
        db: Session,
        user_id: int,
        strategy_code: str,
        signal_data: SignalEntryRequest,
        symbol: SymbolMaster,
        strike_symbol: SymbolMaster,
        position: Position,
        order_type: OrderType,
        qty: int,
        price: Optional[Decimal] = None
    ) -> Order:
        """Create an order record"""
        
        order = Order(
            user_id=user_id,
            position_id=position.id if position else None,
            order_id=f"{user_id}_{signal_data.unique_id}_{datetime.now(EnhancedSignalService.IST).timestamp()}",
            symbol=strike_symbol.symbol,
            underlying=symbol.symbol,
            order_type=order_type,
            product_type=EnhancedSignalService.DEFAULT_PRODUCT_TYPE,
            order_variety="REGULAR",
            qty=qty,
            price=price,
            executed_qty=0,
            pending_qty=qty,
            status=OrderStatus.PENDING,
            exchange=strike_symbol.exchange.value,
            placed_at=datetime.now(EnhancedSignalService.IST)
        )
        
        return order
    
    @staticmethod
    def _get_default_ltp(symbol_type: str = "option") -> Decimal:
        """Get default LTP when actual price is not available"""
        # These are placeholder values - in production, fetch from market data
        if symbol_type == "option":
            return Decimal('100.00')  # Default option premium
        return Decimal('18000.00')  # Default index price
    
    @staticmethod
    def _get_default_qty(user_id: int, db: Session) -> int:
        """Get default quantity for user"""
        # Check user trading settings
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.trading_settings:
            return user.trading_settings.default_qty
        return EnhancedSignalService.DEFAULT_QTY
    
    @staticmethod
    def process_entry_signal(db: Session, signal_data: SignalEntryRequest) -> Dict[str, Any]:
        """
        Process entry signal for all active traders
        
        Args:
            db: Database session
            signal_data: Entry signal data
            
        Returns:
            Dictionary with processed signal information and per-trader results
        """
        try:
            # 1. Log the signal
            signal_log = SignalLog(
                token=signal_data.token,
                signal_type=signal_data.signal,
                unique_id=signal_data.unique_id,
                strike_price_token=signal_data.strike_price_token,
                strategy_code=signal_data.strategy_code,
                signal_category="ENTRY",
                timestamp=datetime.now(EnhancedSignalService.IST)
            )
            db.add(signal_log)
            db.flush()
            
            # 2. Get symbol details
            symbol = EnhancedSignalService._get_symbol_details(db, signal_data.token)
            strike_symbol = EnhancedSignalService._get_strike_symbol_details(
                db, signal_data.strike_price_token
            )
            
            if not symbol:
                raise Exception(f"Symbol not found for token: {signal_data.token}")
            
            # Use default values if strike symbol not found
            if not strike_symbol:
                # Create a temporary strike symbol object with defaults
                strike_symbol = type('obj', (object,), {
                    'symbol': f"{symbol.symbol}_STRIKE",
                    'token': signal_data.strike_price_token,
                    'strike_price': Decimal('0'),
                    'option_type': 'CE',
                    'expiry_date': datetime.now(EnhancedSignalService.IST) + timedelta(days=7),
                    'exchange': symbol.exchange,
                    'lot_size': symbol.lot_size or 1
                })()
            
            # 3. Get active traders
            traders = EnhancedSignalService._get_active_traders(db, signal_data.strategy_code)
            
            # 4. Process for each trader
            trader_results = []
            entry_price = EnhancedSignalService._get_default_ltp("option")
            
            for trader in traders:
                try:
                    # Get quantity for this trader
                    qty = EnhancedSignalService._get_default_qty(trader.id, db)
                    
                    # Create position
                    position = EnhancedSignalService._create_position(
                        db=db,
                        user_id=trader.id,
                        strategy_code=signal_data.strategy_code,
                        signal_data=signal_data,
                        symbol=symbol,
                        strike_symbol=strike_symbol,
                        entry_price=entry_price,
                        qty=qty
                    )
                    db.add(position)
                    db.flush()
                    
                    # Create entry order
                    order_type = OrderType.BUY if signal_data.signal == "BUY_ENTRY" else OrderType.SELL
                    order = EnhancedSignalService._create_order(
                        db=db,
                        user_id=trader.id,
                        strategy_code=signal_data.strategy_code,
                        signal_data=signal_data,
                        symbol=symbol,
                        strike_symbol=strike_symbol,
                        position=position,
                        order_type=order_type,
                        qty=qty,
                        price=entry_price
                    )
                    db.add(order)
                    db.flush()
                    
                    # Update order status to executed (in real scenario, this would be done by order execution service)
                    order.status = OrderStatus.EXECUTED
                    order.executed_qty = qty
                    order.pending_qty = 0
                    order.avg_executed_price = entry_price
                    order.executed_at = datetime.now(EnhancedSignalService.IST)
                    
                    trader_results.append({
                        "user_id": trader.id,
                        "username": trader.username,
                        "position_id": position.id,
                        "order_id": order.order_id,
                        "qty": qty,
                        "entry_price": float(entry_price),
                        "status": "SUCCESS"
                    })
                    
                except Exception as trader_error:
                    trader_results.append({
                        "user_id": trader.id,
                        "username": trader.username,
                        "status": "FAILED",
                        "error": str(trader_error)
                    })
            
            db.commit()
            
            return {
                "signal_log_id": signal_log.id,
                "signal_type": signal_log.signal_type,
                "unique_id": signal_log.unique_id,
                "token": signal_log.token,
                "strike_price_token": signal_log.strike_price_token,
                "strategy_code": signal_log.strategy_code,
                "timestamp": signal_log.timestamp.isoformat(),
                "total_traders": len(traders),
                "successful_entries": len([r for r in trader_results if r["status"] == "SUCCESS"]),
                "failed_entries": len([r for r in trader_results if r["status"] == "FAILED"]),
                "trader_results": trader_results
            }
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to process entry signal: {str(e)}")
    
    @staticmethod
    def process_exit_signal(db: Session, signal_data: SignalExitRequest) -> Dict[str, Any]:
        """
        Process exit signal for all active positions matching the signal
        
        Args:
            db: Database session
            signal_data: Exit signal data
            
        Returns:
            Dictionary with processed signal information and per-trader results
        """
        try:
            # 1. Log the signal
            signal_log = SignalLog(
                token=signal_data.token,
                signal_type=signal_data.signal,
                unique_id=signal_data.unique_id,
                strike_price_token=signal_data.strike_price_token,
                strategy_code=signal_data.strategy_code,
                signal_category="EXIT",
                timestamp=datetime.now(EnhancedSignalService.IST)
            )
            db.add(signal_log)
            db.flush()
            
            # 2. Get symbol details
            symbol = EnhancedSignalService._get_symbol_details(db, signal_data.token)
            strike_symbol = EnhancedSignalService._get_strike_symbol_details(
                db, signal_data.strike_price_token
            )
            
            # 3. Find all open positions matching this signal
            # Match by unique_id or by symbol + strategy
            open_positions = db.query(Position).join(
                Order, Position.id == Order.position_id
            ).filter(
                Position.status == PositionStatus.OPEN,
                Order.order_id.like(f"%{signal_data.unique_id}%")  # Match by unique_id
            ).all()
            
            # If no positions found by unique_id, try matching by symbol
            if not open_positions and strike_symbol:
                open_positions = db.query(Position).filter(
                    Position.status == PositionStatus.OPEN,
                    Position.symbol == strike_symbol.symbol
                ).all()
            
            if not open_positions:
                return {
                    "signal_log_id": signal_log.id,
                    "signal_type": signal_log.signal_type,
                    "unique_id": signal_log.unique_id,
                    "message": "No open positions found to exit",
                    "total_positions": 0,
                    "successful_exits": 0,
                    "failed_exits": 0,
                    "trader_results": []
                }
            
            # 4. Process exit for each position
            trader_results = []
            exit_price = EnhancedSignalService._get_default_ltp("option")
            
            for position in open_positions:
                try:
                    # Create exit order
                    order_type = OrderType.SELL if signal_data.signal == "BUY_EXIT" else OrderType.BUY
                    exit_order = Order(
                        user_id=position.user_id,
                        position_id=position.id,
                        order_id=f"{position.user_id}_EXIT_{signal_data.unique_id}_{datetime.now(EnhancedSignalService.IST).timestamp()}",
                        symbol=position.symbol,
                        underlying=position.underlying,
                        order_type=order_type,
                        product_type=EnhancedSignalService.DEFAULT_PRODUCT_TYPE,
                        order_variety="REGULAR",
                        qty=position.qty,
                        price=exit_price,
                        executed_qty=position.qty,
                        pending_qty=0,
                        avg_executed_price=exit_price,
                        status=OrderStatus.EXECUTED,
                        exchange=strike_symbol.exchange.value if strike_symbol else "NSE",
                        placed_at=datetime.now(EnhancedSignalService.IST),
                        executed_at=datetime.now(EnhancedSignalService.IST)
                    )
                    db.add(exit_order)
                    db.flush()
                    
                    # Update position
                    position.status = PositionStatus.CLOSED
                    position.avg_exit_price = exit_price
                    position.exit_time = datetime.now(EnhancedSignalService.IST)
                    
                    # Calculate P&L
                    if signal_data.signal == "BUY_EXIT":  # Closing a long position
                        pnl = (exit_price - position.avg_entry_price) * position.qty
                    else:  # Closing a short position (SELL_EXIT)
                        pnl = (position.avg_entry_price - exit_price) * position.qty
                    
                    position.realized_pnl = pnl
                    position.total_pnl = pnl
                    position.pnl_percent = (pnl / (position.avg_entry_price * position.qty)) * 100
                    
                    # Create trade record
                    trade = Trade(
                        user_id=position.user_id,
                        position_id=position.id,
                        symbol=position.symbol,
                        underlying=position.underlying,
                        strike_price=position.strike_price,
                        option_type=position.option_type,
                        expiry_date=position.expiry_date,
                        entry_qty=position.qty,
                        entry_price=position.avg_entry_price,
                        entry_time=position.entry_time,
                        exit_qty=position.qty,
                        exit_price=exit_price,
                        exit_time=position.exit_time,
                        gross_pnl=pnl,
                        net_pnl=pnl,  # Simplified, should subtract charges
                        pnl_percent=position.pnl_percent,
                        trade_type="INTRADAY",
                        exit_reason="SIGNAL",
                        holding_time=int((position.exit_time - position.entry_time).total_seconds() / 60)
                    )
                    db.add(trade)
                    
                    trader_results.append({
                        "user_id": position.user_id,
                        "position_id": position.id,
                        "order_id": exit_order.order_id,
                        "qty": position.qty,
                        "entry_price": float(position.avg_entry_price),
                        "exit_price": float(exit_price),
                        "pnl": float(pnl),
                        "pnl_percent": float(position.pnl_percent),
                        "status": "SUCCESS"
                    })
                    
                except Exception as trader_error:
                    trader_results.append({
                        "user_id": position.user_id,
                        "position_id": position.id,
                        "status": "FAILED",
                        "error": str(trader_error)
                    })
            
            db.commit()
            
            return {
                "signal_log_id": signal_log.id,
                "signal_type": signal_log.signal_type,
                "unique_id": signal_log.unique_id,
                "token": signal_log.token,
                "strike_price_token": signal_log.strike_price_token,
                "strategy_code": signal_log.strategy_code,
                "timestamp": signal_log.timestamp.isoformat(),
                "total_positions": len(open_positions),
                "successful_exits": len([r for r in trader_results if r["status"] == "SUCCESS"]),
                "failed_exits": len([r for r in trader_results if r["status"] == "FAILED"]),
                "trader_results": trader_results
            }
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to process exit signal: {str(e)}")
    
    @staticmethod
    def get_active_positions_by_strategy(
        db: Session, 
        strategy_code: str,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all active positions for a strategy
        
        Args:
            db: Database session
            strategy_code: Strategy code to filter
            user_id: Optional user ID filter
            
        Returns:
            List of active positions
        """
        query = db.query(Position).filter(
            Position.status == PositionStatus.OPEN
        )
        
        if user_id:
            query = query.filter(Position.user_id == user_id)
        
        # TODO: Add strategy_code filter when strategy relationship is added
        
        positions = query.all()
        
        return [
            {
                "position_id": pos.id,
                "user_id": pos.user_id,
                "symbol": pos.symbol,
                "underlying": pos.underlying,
                "qty": pos.qty,
                "entry_price": float(pos.avg_entry_price),
                "unrealized_pnl": float(pos.unrealized_pnl),
                "entry_time": pos.entry_time.isoformat()
            }
            for pos in positions
        ]