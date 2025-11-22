
"""
Script to create fake test users and trading data for development/testing
"""

from app.db.db import SessionLocal
from app.models.models import (
    User, Broker, UserBrokerAccount, UserTradingSettings, 
    UserRiskSettings, UserUISettings, UserRole, Strategy, 
    StrategyStatus, Order, OrderType, OrderStatus, Position, 
    PositionStatus, Trade
)
from app.utils.security import SecurityUtils
from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker
import random

fake = Faker()

# ---------------------------------------------------
# 1. Create sample test users for each role (except superadmin)
# ---------------------------------------------------

def create_sample_users(db):
    print("\n🚀 Creating sample users for each role...")
    
    # Define user roles (except SUPERADMIN)
    test_roles = [UserRole.USER, UserRole.TRADER, UserRole.ADMIN]
    created_users = []
    
    for role in test_roles:
        email = f"{role.value.lower()}_test@example.com"
        username = f"{role.value.lower()}_test"
        
        # Avoid duplicates
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"✓ User already exists for role {role.value}: {email}")
            created_users.append(existing)
            continue
        
        # Create user with hashed password
        password_hash = SecurityUtils.hash_password("test123")
        user = User(
            name=f"{role.value.title()} Test User",
            email=email,
            username=username,
            password_hash=password_hash,
            role=role,
            is_active=True,
            is_verified=True,
            kyc_verified=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create user settings
        trading_settings = UserTradingSettings(
            user_id=user.id,
            timezone="Asia/Kolkata",
            auto_square_off=True,
            auto_square_off_time="15:20",
            default_qty=1,
            default_product_type="NRML",
            default_order_type="MARKET"
        )
        db.add(trading_settings)
        
        risk_settings = UserRiskSettings(
            user_id=user.id,
            max_position_size=Decimal("50000.00"),
            max_positions=5,
            max_positions_per_symbol=2,
            daily_loss_limit=Decimal("5000.00"),
            weekly_loss_limit=Decimal("15000.00"),
            monthly_loss_limit=Decimal("50000.00"),
            risk_per_trade=Decimal("2.0"),
            max_drawdown_limit=Decimal("15.0"),
            stop_trading_on_limit=True,
            emergency_exit_on_limit=False
        )
        db.add(risk_settings)
        
        ui_settings = UserUISettings(
            user_id=user.id,
            theme="dark",
            language="en",
            email_notifications=True,
            sms_notifications=True,
            push_notifications=True,
            trade_notifications=True,
            order_notifications=True,
            risk_notifications=True
        )
        db.add(ui_settings)
        
        db.commit()
        
        print(f"✓ Created test user for role {role.value} → {user.email}")
        created_users.append(user)
    
    print("✅ Sample user creation completed.\n")
    return created_users


# ---------------------------------------------------
# 2. Inject Fake Trading Data
# ---------------------------------------------------

def inject_fake_trading_data(db, users):
    print("🚀 Injecting fake trading data...\n")
    
    # Create or get broker
    broker = db.query(Broker).filter(Broker.name == "TestBroker").first()
    if not broker:
        broker = Broker(
            name="TestBroker",
            display_name="Test Broker Ltd",
            description="Test broker for development",
            is_active=True,
            supports_websocket=True
        )
        db.add(broker)
        db.commit()
        db.refresh(broker)
    
    for user in users:
        print(f"📌 Processing fake data for: {user.email}")
        
        # Create broker account if not exists
        broker_account = db.query(UserBrokerAccount).filter(
            UserBrokerAccount.user_id == user.id
        ).first()
        
        if not broker_account:
            broker_account = UserBrokerAccount(
                user_id=user.id,
                broker_id=broker.id,
                broker_client_id=f"TEST{user.id}001",
                api_key=f"test_api_key_{user.id}",
                api_secret=f"test_api_secret_{user.id}",
                is_active=True,
                is_connected=True,
                account_balance=Decimal("100000.00"),
                margin_available=Decimal("80000.00"),
                margin_used=Decimal("20000.00")
            )
            db.add(broker_account)
            db.commit()
        
        # Create strategy
        strategy = Strategy(
            user_id=user.id,
            name=f"{user.username}_auto_strategy",
            description="Auto-generated test strategy",
            strategy_type="STRADDLE",
            underlying=random.choice(["NIFTY", "BANKNIFTY"]),
            timeframe="5m",
            status=StrategyStatus.ACTIVE,
            max_positions=3,
            position_size=Decimal("25000.00"),
            is_live=False
        )
        db.add(strategy)
        db.commit()
        db.refresh(strategy)
        
        now = datetime.now()
        expiry_date = now + timedelta(days=7)
        
        # ----------------------------
        # Fake orders
        # ----------------------------
        for i in range(3):
            underlying = random.choice(["NIFTY", "BANKNIFTY"])
            strike = random.choice([21000, 21100, 45000, 45500])
            opt_type = random.choice(["CE", "PE"])
            symbol = f"{underlying}{expiry_date.strftime('%d%b%y').upper()}{strike}{opt_type}"
            
            order = Order(
                user_id=user.id,
                strategy_id=strategy.id,
                order_id=fake.uuid4()[:20],
                symbol=symbol,
                underlying=underlying,
                order_type=random.choice([OrderType.BUY, OrderType.SELL]),
                product_type="NRML",
                qty=random.choice([25, 50, 75]),
                price=Decimal(str(round(random.uniform(100, 300), 2))),
                executed_qty=random.choice([0, 25, 50]),
                status=random.choice([OrderStatus.EXECUTED, OrderStatus.PENDING, OrderStatus.CANCELLED]),
                broker_order_id=fake.uuid4()[:15],
                exchange="NSE",
                placed_at=now - timedelta(hours=random.randint(1, 24))
            )
            db.add(order)
            print(f"  ⇒ Created Order: {symbol} {order.order_type.value}")
        
        # ----------------------------
        # Fake positions
        # ----------------------------
        for i in range(2):
            underlying = random.choice(["NIFTY", "BANKNIFTY"])
            strike = random.choice([21000, 21100, 45000, 45500])
            opt_type = random.choice(["CE", "PE"])
            symbol = f"{underlying}{expiry_date.strftime('%d%b%y').upper()}{strike}{opt_type}"
            entry_price = round(random.uniform(100, 300), 2)
            current_price = entry_price * random.uniform(0.9, 1.1)
            qty = random.choice([25, 50, 75])
            pnl = (current_price - entry_price) * qty
            
            position = Position(
                user_id=user.id,
                strategy_id=strategy.id,
                symbol=symbol,
                underlying=underlying,
                strike_price=strike,
                option_type=opt_type,
                expiry_date=expiry_date,
                qty=qty,
                avg_entry_price=Decimal(str(entry_price)),
                current_price=Decimal(str(current_price)),
                unrealized_pnl=Decimal(str(pnl)),
                total_pnl=Decimal(str(pnl)),
                status=PositionStatus.OPEN,
                entry_time=now - timedelta(hours=random.randint(1, 12))
            )
            db.add(position)
            print(f"  ⇒ Created Position: {symbol} PnL: ₹{pnl:.2f}")
        
        # ----------------------------
        # Fake completed trades
        # ----------------------------
        for i in range(3):
            underlying = random.choice(["NIFTY", "BANKNIFTY"])
            strike = random.choice([21000, 21100, 45000, 45500])
            opt_type = random.choice(["CE", "PE"])
            symbol = f"{underlying}{expiry_date.strftime('%d%b%y').upper()}{strike}{opt_type}"
            entry_price = round(random.uniform(100, 300), 2)
            exit_price = entry_price * random.uniform(0.85, 1.15)
            qty = random.choice([25, 50, 75])
            gross_pnl = (exit_price - entry_price) * qty
            net_pnl = gross_pnl - (qty * 0.80)  # Simple brokerage deduction
            
            entry_time = now - timedelta(days=random.randint(1, 7))
            exit_time = entry_time + timedelta(hours=random.randint(1, 8))
            
            trade = Trade(
                user_id=user.id,
                strategy_id=strategy.id,
                symbol=symbol,
                underlying=underlying,
                strike_price=strike,
                option_type=opt_type,
                expiry_date=expiry_date,
                entry_qty=qty,
                entry_price=Decimal(str(entry_price)),
                entry_time=entry_time,
                entry_order_id=fake.uuid4()[:15],
                exit_qty=qty,
                exit_price=Decimal(str(exit_price)),
                exit_time=exit_time,
                exit_order_id=fake.uuid4()[:15],
                gross_pnl=Decimal(str(gross_pnl)),
                brokerage=Decimal(str(qty * 0.50)),
                net_pnl=Decimal(str(net_pnl)),
                trade_type="INTRADAY",
                exit_reason=random.choice(["TARGET", "STOPLOSS", "MANUAL"])
            )
            db.add(trade)
            print(f"  ⇒ Created Trade: {symbol} Net PnL: ₹{net_pnl:.2f}")
        
        db.commit()
        print()
    
    print("✅ Fake trading data injection completed.\n")


# ---------------------------------------------------
# 3. Main Execution Function
# ---------------------------------------------------

def run_fake_data_process():
    db = SessionLocal()
    try:
        sample_users = create_sample_users(db)
        inject_fake_trading_data(db, sample_users)
        print("🎉 All fake data created successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


# ---------------------------------------------------
# 4. Call this from your script entry point
# ---------------------------------------------------

if __name__ == "__main__":
    run_fake_data_process()
