"""
Trade service - Business logic for trade operations
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.models import Trade
from app.schemas.schema import TradeCreate, TradeUpdate

logger = logging.getLogger(__name__)


class TradeService:
    """Service for trade operations"""

    @staticmethod
    def get_all_trades(db: Session, user_id: Optional[int] = None) -> List[Trade]:
        """Get all trades, optionally filtered by user"""
        try:
            query = db.query(Trade)
            if user_id:
                query = query.filter(Trade.user_id == user_id)
            trades = query.all()
            logger.info(f"Retrieved {len(trades)} trades")
            return trades
        except Exception as e:
            logger.error(f"Error retrieving trades: {str(e)}")
            raise

    @staticmethod
    def get_trade_by_id(db: Session, trade_id: int) -> Optional[Trade]:
        """Get trade by ID"""
        try:
            trade = db.query(Trade).filter(Trade.id == trade_id).first()
            if trade:
                logger.info(f"Retrieved trade: {trade_id}")
            return trade
        except Exception as e:
            logger.error(f"Error retrieving trade {trade_id}: {str(e)}")
            raise

    @staticmethod
    def create_trade(db: Session, trade_data: TradeCreate) -> Trade:
        """Create master trade, then execute orders for all active users"""
        from app.models.models import AngelOneCredentials, DhanCredentials, User, Order, OrderStatus, OrderType
        from app.services.broker_services import place_angelone_order_standalone, place_dhan_order_standalone
        import concurrent.futures

        try:
            # 1. Create Master Trade (Signal Record)
            # Remove user_id from trade_data if present (it shouldn't be in TradeCreate but just in case)
            trade_dict = trade_data.dict()
            
            # Initial PnL 0
            pnl = 0
            pnl_percent = 0
            
            master_trade = Trade(
                **trade_dict,
                pnl=pnl,
                pnl_percent=pnl_percent
                # user_id is removed
            )
            db.add(master_trade)
            db.commit()
            db.refresh(master_trade)
            logger.info(f"Created Master Trade: {master_trade.id}")

            # 2. Fetch All Active Users
            # Ensure we get users who have trading enabled or are 'TRADER' role?
            # For now, get all active users who are not SUPERADMIN maybe? Or just all active users.
            # Assuming logic: All active users get the trade.
            active_users = db.query(User).filter(User.is_active == True).all()

            broker_responses = []

            # 3. Define Execution Helper (Per User)
            def process_user_order(user):
                order_responses = []
                
                # A. Fetch Credentials
                angel_creds = db.query(AngelOneCredentials).filter(
                    AngelOneCredentials.user_id == user.id, 
                    AngelOneCredentials.is_active == True
                ).first()
                
                dhan_creds = db.query(DhanCredentials).filter(
                    DhanCredentials.user_id == user.id, 
                    DhanCredentials.is_active == True
                ).first()

                # B. Execute Angel Order
                if angel_creds:
                    try:
                        params = {
                            "variety": "NORMAL",
                            "tradingsymbol": trade_data.symbol,
                            "symboltoken": str(trade_data.strike_price),
                            "transactiontype": "BUY",
                            "exchange": "NSE",
                            "ordertype": "MARKET",
                            "producttype": "INTRADAY",
                            "duration": "DAY",
                            "price": "0",
                            "quantity": str(trade_data.entry_qty)
                        }
                        # CALL BROKER
                        response = place_angelone_order_standalone(
                            api_key=angel_creds.api_key,
                            username=angel_creds.username,
                            pwd=angel_creds.password,
                            token=angel_creds.token,
                            order_params=params
                        )
                        
                        # CREATE ORDER RECORD
                        angel_order = Order(
                            user_id=user.id,
                            trade_id=master_trade.id,
                            symbol=trade_data.symbol,
                            underlying=trade_data.underlying,
                            order_type=OrderType.BUY, # Assuming Entry is BUY
                            qty=trade_data.entry_qty,
                            price=0, # Market Order
                            status=OrderStatus.PLACED if response.get('status') else OrderStatus.REJECTED,
                            broker_order_id=response.get('data', {}).get('orderid'),
                            exchange="NSE",
                            status_message=str(response)
                        )
                        db.add(angel_order)
                        order_responses.append({"user": user.id, "broker": "AngelOne", "status": "Sent"})
                    except Exception as ex:
                        logger.error(f"User {user.id} Angel Exec Failed: {ex}")
                        order_responses.append({"user": user.id, "broker": "AngelOne", "error": str(ex)})

                # C. Execute Dhan Order
                if dhan_creds:
                    try:
                        params = {
                            "security_id": str(trade_data.strike_price),
                            "exchange_segment": "NSE_EQ", 
                            "transaction_type": "BUY",
                            "order_type": "MARKET",
                            "product_type": "INTRA",
                            "quantity": trade_data.entry_qty,
                            "price": 0
                        }
                        # CALL BROKER
                        response = place_dhan_order_standalone(
                            client_id=dhan_creds.client_id,
                            access_token=dhan_creds.access_token,
                            order_params=params
                        )
                        
                        # CREATE ORDER RECORD
                        dhan_order = Order(
                            user_id=user.id,
                            trade_id=master_trade.id,
                            symbol=trade_data.symbol,
                            underlying=trade_data.underlying,
                            order_type=OrderType.BUY,
                            qty=trade_data.entry_qty,
                            price=0,
                            status=OrderStatus.PLACED if response.get('status') else OrderStatus.REJECTED,
                            broker_order_id=response.get('data', {}).get('orderId'),
                            exchange="NSE",
                            status_message=str(response)
                        )
                        db.add(dhan_order)
                        order_responses.append({"user": user.id, "broker": "Dhan", "status": "Sent"})
                    except Exception as ex:
                        logger.error(f"User {user.id} Dhan Exec Failed: {ex}")
                        order_responses.append({"user": user.id, "broker": "Dhan", "error": str(ex)})
                
                return order_responses

            # 4. Execute for All Users Parallelly
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(process_user_order, user) for user in active_users]
                for future in concurrent.futures.as_completed(futures):
                    broker_responses.extend(future.result())

            db.commit() # Commit all new orders
            logger.info(f"Master Trade {master_trade.id} execution completed. Responses: {broker_responses}")
            return master_trade

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating trade: {str(e)}")
            raise

    @staticmethod
    def update_trade(db: Session, trade_id: int, trade_data: TradeUpdate) -> Optional[Trade]:
        """Update trade"""
        try:
            trade = db.query(Trade).filter(Trade.id == trade_id).first()
            if not trade:
                logger.warning(f"Trade not found: {trade_id}")
                return None
            
            # Recalculate PnL if price changed
            if trade_data.current_price:
                pnl = (trade_data.current_price - trade.entry_price) * trade.qty
                pnl_percent = ((trade_data.current_price - trade.entry_price) / trade.entry_price) * 100
                trade.pnl = pnl
                trade.pnl_percent = pnl_percent
            
            update_data = trade_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                if key not in ['pnl', 'pnl_percent']:
                    setattr(trade, key, value)
            
            db.commit()
            db.refresh(trade)
            logger.info(f"Updated trade: {trade_id}")
            return trade
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating trade {trade_id}: {str(e)}")
            raise

    @staticmethod
    def delete_trade(db: Session, trade_id: int) -> bool:
        """Delete trade"""
        try:
            trade = db.query(Trade).filter(Trade.id == trade_id).first()
            if not trade:
                logger.warning(f"Trade not found: {trade_id}")
                return False
            
            db.delete(trade)
            db.commit()
            logger.info(f"Deleted trade: {trade_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting trade {trade_id}: {str(e)}")
            raise

    @staticmethod
    def get_active_trades(db: Session, user_id: int) -> List[Trade]:
        """Get active trades for user"""
        try:
            trades = db.query(Trade).filter(
                Trade.user_id == user_id,
                Trade.status == "ACTIVE"
            ).all()
            logger.info(f"Retrieved {len(trades)} active trades for user: {user_id}")
            return trades
        except Exception as e:
            logger.error(f"Error retrieving active trades: {str(e)}")
            raise

    @staticmethod
    def close_trade(db: Session, trade_id: int, closing_price: float = 0) -> Optional[Trade]:
        """Close master trade and execute exit orders for all participating users"""
        from app.models.models import AngelOneCredentials, DhanCredentials, Order, OrderType, OrderStatus
        from app.services.broker_services import place_angelone_order_standalone, place_dhan_order_standalone
        import concurrent.futures

        try:
            # 1. Fetch Master Trade
            trade = db.query(Trade).filter(Trade.id == trade_id).first()
            if not trade:
                logger.warning(f"Trade not found: {trade_id}")
                return None
            
            # 2. Identify Participating Users (Those who have a BUY order for this trade)
            # Distinct users who have placed an order for this trade
            participating_user_ids = [
                order.user_id for order in db.query(Order.user_id).filter(
                    Order.trade_id == trade_id,
                    Order.order_type == OrderType.BUY
                ).distinct()
            ]

            logger.info(f"Closing Trade {trade_id} for users: {participating_user_ids}")
            
            broker_responses = []

            # 3. Define Execution Helper (Per User)
            def process_user_exit(user_id):
                exit_responses = []
                
                # A. Fetch Credentials
                angel_creds = db.query(AngelOneCredentials).filter(
                    AngelOneCredentials.user_id == user_id, 
                    AngelOneCredentials.is_active == True
                ).first()
                
                dhan_creds = db.query(DhanCredentials).filter(
                    DhanCredentials.user_id == user_id, 
                    DhanCredentials.is_active == True
                ).first()

                # B. Execute Angel Exit
                if angel_creds:
                    try:
                        params = {
                            "variety": "NORMAL",
                            "tradingsymbol": trade.symbol,
                            "symboltoken": str(trade.strike_price),
                            "transactiontype": "SELL", # SELL for Exit
                            "exchange": "NSE",
                            "ordertype": "MARKET",
                            "producttype": "INTRADAY",
                            "duration": "DAY",
                            "price": "0",
                            "quantity": str(trade.entry_qty) # Assuming full exit
                        }
                        # CALL BROKER
                        response = place_angelone_order_standalone(
                            api_key=angel_creds.api_key,
                            username=angel_creds.username,
                            pwd=angel_creds.password,
                            token=angel_creds.token,
                            order_params=params
                        )
                        
                        # CREATE EXIT ORDER RECORD
                        angel_order = Order(
                            user_id=user_id,
                            trade_id=trade.id,
                            symbol=trade.symbol,
                            underlying=trade.underlying,
                            order_type=OrderType.SELL, # EXIT
                            qty=trade.entry_qty,
                            price=0,
                            status=OrderStatus.PLACED if response.get('status') else OrderStatus.REJECTED,
                            broker_order_id=response.get('data', {}).get('orderid'),
                            exchange="NSE",
                            status_message=str(response)
                        )
                        db.add(angel_order)
                        exit_responses.append({"user": user_id, "broker": "AngelOne", "status": "Sent"})
                    except Exception as ex:
                        logger.error(f"User {user_id} Angel Exit Failed: {ex}")
                        exit_responses.append({"user": user_id, "broker": "AngelOne", "error": str(ex)})

                # C. Execute Dhan Exit
                if dhan_creds:
                    try:
                        params = {
                            "security_id": str(trade.strike_price),
                            "exchange_segment": "NSE_EQ", 
                            "transaction_type": "SELL", # SELL for Exit
                            "order_type": "MARKET",
                            "product_type": "INTRA",
                            "quantity": trade.entry_qty,
                            "price": 0
                        }
                        # CALL BROKER
                        response = place_dhan_order_standalone(
                            client_id=dhan_creds.client_id,
                            access_token=dhan_creds.access_token,
                            order_params=params
                        )
                        
                        # CREATE EXIT ORDER RECORD
                        dhan_order = Order(
                            user_id=user_id,
                            trade_id=trade.id,
                            symbol=trade.symbol,
                            underlying=trade.underlying,
                            order_type=OrderType.SELL, # EXIT
                            qty=trade.entry_qty,
                            price=0,
                            status=OrderStatus.PLACED if response.get('status') else OrderStatus.REJECTED,
                            broker_order_id=response.get('data', {}).get('orderId'),
                            exchange="NSE",
                            status_message=str(response)
                        )
                        db.add(dhan_order)
                        exit_responses.append({"user": user_id, "broker": "Dhan", "status": "Sent"})
                    except Exception as ex:
                        logger.error(f"User {user_id} Dhan Exit Failed: {ex}")
                        exit_responses.append({"user": user_id, "broker": "Dhan", "error": str(ex)})
                
                return exit_responses

            # 4. Execute for All Participating Users Parallelly
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(process_user_exit, uid) for uid in participating_user_ids]
                for future in concurrent.futures.as_completed(futures):
                    broker_responses.extend(future.result())

            # 5. Update Master Trade to CLOSED
            trade.current_price = closing_price # Optional reference
            trade.status = "CLOSED"
            # Logic for PnL on Master Trade is ambiguous without a single exit price, 
            # maybe just average or leave as is. User said "entries for required tables", 
            # so Order table entries above cover the critical part.
            
            db.commit()
            logger.info(f"Closed Trade {trade_id}. Responses: {broker_responses}")
            return trade

        except Exception as e:
            db.rollback()
            logger.error(f"Error closing trade {trade_id}: {str(e)}")
            raise
