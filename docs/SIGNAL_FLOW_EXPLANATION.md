# Signal Processing Flow - Complete Explanation

## 📡 When You Receive a Signal from Your External System

Here's **exactly what happens** step-by-step when your external trading system sends a signal:

---

## 🔄 **ENTRY SIGNAL FLOW** (BUY_ENTRY / SELL_ENTRY)

### Step 1: External System Sends Signal

Your external system sends a POST request to:

```
POST /db/signals/v2/entry
```

**Request Body:**

```json
{
  "token": "23", // Spot symbol token (e.g., NIFTY)
  "signal": "BUY_ENTRY", // Signal type
  "unique_id": "unique_123", // Unique identifier for this trade
  "strike_price_token": "45678", // Option strike token
  "strategy_code": "STRATEGY_001" // Your strategy identifier
}
```

---

### Step 2: Signal Controller Receives Request

📍 **File**: `signal_controller.py` (Line 108-178)

- API endpoint `/v2/entry` receives the signal
- Calls `EnhancedSignalService.process_entry_signal()`

---

### Step 3: Signal Logging

📍 **File**: `enhanced_signal_services.py` (Lines 171-181)

✅ **Creates SignalLog record:**

```python
SignalLog(
    token="23",
    signal_type="BUY_ENTRY",
    unique_id="unique_123",
    strike_price_token="45678",
    strategy_code="STRATEGY_001",
    signal_category="ENTRY",
    timestamp=now()
)
```

**Purpose**: Permanent record of every signal received

---

### Step 4: Symbol Lookup

📍 **File**: `enhanced_signal_services.py` (Lines 183-203)

✅ **Looks up symbols from SymbolMaster table:**

- Spot symbol (token="23") → Gets NIFTY details
- Strike symbol (token="45678") → Gets option details (CE/PE, strike price, expiry)

---

### Step 5: Get Active Traders

📍 **File**: `enhanced_signal_services.py` (Lines 206)

✅ **Finds all active traders:**

```python
traders = db.query(User).filter(
    User.is_active == True,
    User.role in [TRADER, ADMIN, SUPERADMIN],
    User.kyc_verified == True
).all()
```

**Example**: If you have 5 active traders, all 5 will receive this signal

---

### Step 6: For EACH Trader - Create Position

📍 **File**: `enhanced_signal_services.py` (Lines 217-229)

✅ **Creates Position record for each trader:**

```python
Position(
    user_id=trader.id,
    symbol="NIFTY23DEC23500CE",      // Option symbol
    underlying="NIFTY",               // Underlying index
    strike_price=23500,
    option_type="CE",
    expiry_date="2023-12-23",
    qty=1,                            // From user settings
    avg_entry_price=100.00,           // Current LTP
    status=OPEN,
    entry_time=now(),
    stop_loss=95.00,                  // Auto: 5% below entry
    target=110.00,                    // Auto: 10% above entry
    margin_used=100.00
)
```

**Purpose**: Tracks the open position for this trader

---

### Step 7: For EACH Trader - Create Entry Order

📍 **File**: `enhanced_signal_services.py` (Lines 231-246)

✅ **Creates Order record:**

```python
Order(
    user_id=trader.id,
    position_id=position.id,
    order_id="1_unique_123_1234567890.123",
    symbol="NIFTY23DEC23500CE",
    order_type=BUY,                   // BUY for BUY_ENTRY
    product_type="NRML",
    qty=1,
    price=100.00,
    executed_qty=1,
    status=EXECUTED,                  // Marked as executed
    placed_at=now(),
    executed_at=now()
)
```

**Purpose**: Records the order execution

---

### Step 8: Response Sent Back

📍 **File**: `signal_controller.py` (Lines 168-172)

✅ **Returns response:**

```json
{
  "success": true,
  "message": "Entry signal processed for 5 traders",
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
      // ... 4 more traders
    ]
  }
}
```

---

## 🔄 **EXIT SIGNAL FLOW** (BUY_EXIT / SELL_EXIT)

### Step 1: External System Sends Exit Signal

```
POST /db/signals/v2/exit
```

**Request Body:**

```json
{
  "token": "23",
  "signal": "BUY_EXIT", // Exit the position
  "unique_id": "unique_123", // SAME unique_id as entry
  "strike_price_token": "45678",
  "strategy_code": "STRATEGY_001"
}
```

---

### Step 2: Find Open Positions

📍 **File**: `enhanced_signal_services.py` (Lines 327-339)

✅ **Finds all open positions matching this signal:**

```python
positions = db.query(Position).filter(
    Position.status == OPEN,
    Order.order_id.like("%unique_123%")  // Matches by unique_id
).all()
```

**Example**: Finds all 5 positions created by the entry signal

---

### Step 3: For EACH Position - Create Exit Order

📍 **File**: `enhanced_signal_services.py` (Lines 359-381)

✅ **Creates exit order:**

```python
Order(
    user_id=position.user_id,
    position_id=position.id,
    order_id="1_EXIT_unique_123_1234567890.456",
    symbol="NIFTY23DEC23500CE",
    order_type=SELL,                  // SELL for BUY_EXIT
    qty=1,
    price=110.00,                     // Current exit price
    status=EXECUTED
)
```

---

### Step 4: Close Position & Calculate P&L

📍 **File**: `enhanced_signal_services.py` (Lines 383-396)

✅ **Updates position:**

```python
position.status = CLOSED
position.avg_exit_price = 110.00
position.exit_time = now()

// Calculate P&L
pnl = (exit_price - entry_price) * qty
    = (110.00 - 100.00) * 1
    = 10.00

position.realized_pnl = 10.00
position.total_pnl = 10.00
position.pnl_percent = 10.0%
```

---

### Step 5: Create Trade Record

📍 **File**: `enhanced_signal_services.py` (Lines 399-420)

✅ **Creates Trade record (completed trade):**

```python
Trade(
    user_id=position.user_id,
    position_id=position.id,
    symbol="NIFTY23DEC23500CE",
    underlying="NIFTY",
    strike_price=23500,
    option_type="CE",
    entry_qty=1,
    entry_price=100.00,
    entry_time="2025-12-15 09:30:00",
    exit_qty=1,
    exit_price=110.00,
    exit_time="2025-12-15 15:20:00",
    gross_pnl=10.00,
    net_pnl=10.00,
    pnl_percent=10.0,
    trade_type="INTRADAY",
    exit_reason="SIGNAL",
    holding_time=350                  // minutes
)
```

**Purpose**: Permanent record of completed trade for analytics

---

### Step 6: Response Sent Back

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
        "order_id": "1_EXIT_unique_123_1234567890.456",
        "qty": 1,
        "entry_price": 100.0,
        "exit_price": 110.0,
        "pnl": 10.0,
        "pnl_percent": 10.0,
        "status": "SUCCESS"
      }
      // ... 4 more traders
    ]
  }
}
```

---

## 📊 **Database Tables Updated**

### On ENTRY Signal:

1. ✅ **SignalLog** - 1 record (signal received)
2. ✅ **Position** - 5 records (one per trader, status=OPEN)
3. ✅ **Order** - 5 records (entry orders, status=EXECUTED)

### On EXIT Signal:

1. ✅ **SignalLog** - 1 record (exit signal received)
2. ✅ **Position** - 5 records updated (status=CLOSED, P&L calculated)
3. ✅ **Order** - 5 new records (exit orders, status=EXECUTED)
4. ✅ **Trade** - 5 new records (completed trades with P&L)

---

## 🎯 **Key Points**

### Multi-Trader Support:

- ✅ One signal → Multiple traders get positions
- ✅ Each trader has their own Position, Order, and Trade records
- ✅ Traders can have different quantities based on their settings

### Automatic Features:

- ✅ Auto stop-loss: 5% below entry price
- ✅ Auto target: 10% above entry price
- ✅ Auto P&L calculation on exit
- ✅ Auto trade record creation

### Signal Matching:

- ✅ Entry and Exit matched by `unique_id`
- ✅ Ensures correct positions are closed
- ✅ Prevents closing wrong positions

### Trade Table Purpose:

- ✅ **NOT UNUSED** - Critical for recording completed trades
- ✅ Used for analytics, reporting, P&L history
- ✅ Created automatically on every exit signal

---

## 🔗 **API Endpoints**

```
POST /db/signals/v2/entry   → Process entry signal
POST /db/signals/v2/exit    → Process exit signal
GET  /db/signals/v2/active-positions?strategy_code=XXX → View open positions
```

---

## 💡 **Summary**

When your external system sends a signal:

1. **Entry Signal** → Creates positions and orders for all active traders
2. **Exit Signal** → Closes positions, calculates P&L, creates trade records
3. **Trade Table** → Stores completed trades for history and analytics

**The Trade table is ESSENTIAL and should NOT be dropped!**
