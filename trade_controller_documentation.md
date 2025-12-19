# Trade Controller Documentation

## Overview

The `TradeController` (`app/controllers/trade_controller.py`) manages the lifecycle of **Master Trades**. It exposes API endpoints for creating, retrieving, updating, deleting, and closing trades.

> [!IMPORTANT] > **Master Trade Concept**: A "Trade" record now represents a **Global Signal** (Master Trade). It is not specific to a single user.
>
> - **Creation**: When a Master Trade is created, the system automatically executes distinct orders for all active users.
> - **Closing**: When a Master Trade is closed, the system automatically triggers exit orders for all participating users.

## Authentication & Authorization

All endpoints require a valid JWT access token.

- **Dependency**: `get_current_user`
- **Role-Based Access Control (RBAC)**:
  - **ADMIN / SUPERADMIN**: Can Create, Update, Delete, and Close Master Trades.
  - **TRADER / USER**: Can only view active trades relevant to them (via `active/all` or specific IDs if authorized).

---

## API Endpoints

### 1. Create Master Trade (Signal Entry)

Creates a new Master Trade and triggers **BUY** orders for all active users.

- **URL**: `/api/trades`
- **Method**: `POST`
- **Access**: `ADMIN`, `SUPERADMIN`

#### Request Payload (`TradeCreate`)

```json
{
  "symbol": "NIFTY",
  "underlying": "NIFTY",
  "strike_price": 24500,
  "option_type": "CE",
  "expiry_date": "2025-12-25T15:30:00Z",
  "entry_qty": 50,
  "entry_price": 120.5,
  "entry_time": "2025-12-17T09:15:00Z",
  "exit_qty": 0,
  "exit_price": 0,
  "exit_time": null,
  "exit_order_id": null
}
```

| Field          | Type     | Description                                        |
| :------------- | :------- | :------------------------------------------------- |
| `symbol`       | string   | Trading symbol (e.g., "NIFTY25DEC24500CE")         |
| `underlying`   | string   | Underlying asset name (e.g., "NIFTY", "BANKNIFTY") |
| `strike_price` | integer  | Strike price of the option                         |
| `option_type`  | string   | "CE" (Call) or "PE" (Put)                          |
| `expiry_date`  | datetime | Expiration date of the contract                    |
| `entry_qty`    | integer  | Quantity to buy (Lot size \* Lots)                 |
| `entry_price`  | float    | Estimated or actual entry price                    |
| `entry_time`   | datetime | Timestamp of the entry signal                      |

#### Success Response (201 Created)

```json
{
  "data": {
    "id": 101,
    "strategy_id": null,
    "position_id": null,
    "signal_id": null,
    "symbol": "NIFTY",
    "underlying": "NIFTY",
    "strike_price": 24500,
    "option_type": "CE",
    "expiry_date": "2025-12-25T15:30:00Z",
    "entry_qty": 50,
    "entry_price": 120.5,
    "entry_time": "2025-12-17T09:15:00Z",
    "exit_qty": 0,
    "exit_price": 0,
    "exit_time": null,
    "gross_pnl": 0,
    "net_pnl": 0,
    "pnl_percent": 0,
    "status": "ACTIVE",
    "created_at": "2025-12-17T09:15:05Z"
  },
  "status": 201,
  "message": "Trade created successfully"
}
```

---

### 2. Close Master Trade (Signal Exit)

Closes an existing Master Trade and triggers **SELL** orders for all participating users.

- **URL**: `/api/trades/{trade_id}/close`
- **Method**: `POST`
- **Access**: `ADMIN`, `SUPERADMIN`
- **Query Parameters**:
  - `closing_price` (float): The price at which the trade is closed (reference price).

#### Request Example (URL)

```
POST /api/trades/101/close?closing_price=145.00
```

#### Success Response (200 OK)

```json
{
  "data": {
    "id": 101,
    "symbol": "NIFTY",
    "status": "CLOSED",
    "exit_price": 0, // Note: Depends on logic update
    "current_price": 145.0,
    "gross_pnl": 1225.0, // Calculated based on closing_price
    "net_pnl": 1200.0,
    "pnl_percent": 20.33,
    "created_at": "2025-12-17T09:15:05Z"
  },
  "status": 200,
  "message": "Trade closed successfully"
}
```

---

### 3. Get Active Trades

Retrieves a list of all currently active Master Trades.

- **URL**: `/api/trades/active/all`
- **Method**: `GET`
- **Access**: `Authenticated Users`

#### Success Response (200 OK)

```json
{
  "data": [
    {
      "id": 102,
      "symbol": "BANKNIFTY",
      "status": "ACTIVE",
      "entry_price": 320.0,
      "current_price": 335.0,
      "pnl_percent": 4.6
    }
  ],
  "status": 200,
  "message": "Active trades retrieved successfully"
}
```

---

## Backend Process Flow

### Entry Process (Sequence)

1.  **Admin** calls `POST /api/trades` with trade details.
2.  **TradeService** creates a `Trade` record in the database (Status: ACTIVE).
3.  **TradeService** queries `users` table for all users with `is_active=True`.
4.  **Parallel Execution**:
    - Loops through each user.
    - Checks for `AngelOneCredentials` and `DhanCredentials`.
    - **API Call**: Sends "BUY" order to Broker API (Angel/Dhan) with `entry_qty`.
    - **DB Insert**: Creates a new `Order` record linked to the `Trade` (`trade_id`) and `User` (`user_id`).
5.  **Response**: Returns the created Master Trade object.

### Exit Process (Sequence)

1.  **Admin** calls `POST /api/trades/{id}/close`.
2.  **TradeService** fetches the `Trade` record.
3.  **TradeService** queries `orders` table to find all unique `user_id`s that have an order with `trade_id={id}` and `type=BUY`.
4.  **Parallel Execution**:
    - Loops through each participating `user_id`.
    - Fetches Credentials.
    - **API Call**: Sends "SELL" order to Broker API.
    - **DB Insert**: Creates a new `Order` record (Type: SELL) linked to the `Trade` and `User`.
5.  **DB Update**: Sets Master Trade status to `CLOSED` and updates PnL based on `closing_price`.
6.  **Response**: Returns the closed Master Trade object.
