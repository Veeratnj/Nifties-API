# AlgoFlow Terminal - API Documentation

## Overview

AlgoFlow Terminal uses a RESTful API architecture built with JSON Server (for development/mock data) and Axios for HTTP client requests. All API calls follow standard REST conventions with proper status codes, error handling, and response formatting.

**Base URL (Development):** `http://localhost:3001`

---

## Getting Started

### Setup

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Development Servers**
   ```bash
   # Option 1: Run both frontend and API server together
   npm run dev:all

   # Option 2: Run servers separately
   npm run dev          # Frontend on http://localhost:5173
   npm run dev:api      # API on http://localhost:3001
   ```

### Environment Configuration

Create a `.env.local` file in the root directory:

```env
VITE_API_URL=http://localhost:3001
```

---

## API Authentication

All API requests include an optional Authorization header when a token is present:

```
Authorization: Bearer {token}
```

The token is stored in `localStorage` as `af_token` and is automatically included in all requests via the axios interceptor.

---

## Response Format

### Success Response
All successful responses follow this format:

```json
{
  "data": [],
  "status": 200,
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "message": "Error description",
  "status": 400,
  "data": null
}
```

### Status Codes
- **200**: OK - Successful GET, PUT, PATCH
- **201**: Created - Successful POST
- **204**: No Content - Successful DELETE
- **400**: Bad Request - Invalid parameters
- **401**: Unauthorized - Missing or invalid token
- **404**: Not Found - Resource not found
- **500**: Internal Server Error - Server error

---

## API Endpoints

### Market Data Endpoints

#### Get Market Indices
Returns all market indices data.

```
GET /marketIndices
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "NIFTY 50",
    "value": 21894.50,
    "change": 125.30,
    "changePercent": 0.58,
    "isPositive": true,
    "timestamp": "2025-01-17T15:30:00Z"
  }
]
```

**Usage Example:**
```typescript
import { marketApi } from '@/lib/api';

const indices = await marketApi.getIndices();
```

---

#### Get P&L Data
Returns Profit & Loss data for different time periods.

```
GET /pnl
```

**Response:**
```json
[
  {
    "id": 1,
    "period": "today",
    "value": 12450,
    "isPositive": true,
    "description": "+8.5% from yesterday",
    "trades": 8
  },
  {
    "id": 2,
    "period": "week",
    "value": 45230,
    "isPositive": true,
    "description": "12 winning trades",
    "trades": 12
  },
  {
    "id": 3,
    "period": "month",
    "value": 123450,
    "isPositive": true,
    "description": "45 total trades",
    "trades": 45
  }
]
```

**Usage Example:**
```typescript
import { marketApi } from '@/lib/api';

const pnlData = await marketApi.getPnl();
```

---

### Trades Endpoints

#### Get All Trades
Returns all active and historical trades.

```
GET /trades
```

**Response:**
```json
[
  {
    "id": 1,
    "symbol": "NIFTY 21900 CE",
    "index": "NIFTY",
    "strike": 21900,
    "type": "CE",
    "qty": 50,
    "entryPrice": 125.50,
    "currentPrice": 142.30,
    "pnl": 840,
    "pnlPercent": 13.4,
    "status": "ACTIVE",
    "strategy": "Straddle Strategy",
    "timestamp": "10:15 AM",
    "createdAt": "2025-01-17T10:15:00Z"
  }
]
```

**Usage Example:**
```typescript
import { tradesApi } from '@/lib/api';

const trades = await tradesApi.getAll();
```

---

#### Get Trade by ID
```
GET /trades/:id
```

**Usage Example:**
```typescript
const trade = await tradesApi.getById(1);
```

---

#### Create New Trade
```
POST /trades
```

**Request Body:**
```json
{
  "symbol": "NIFTY 21900 CE",
  "index": "NIFTY",
  "strike": 21900,
  "type": "CE",
  "qty": 50,
  "entryPrice": 125.50,
  "currentPrice": 142.30,
  "status": "ACTIVE",
  "strategy": "Straddle Strategy",
  "timestamp": "10:15 AM"
}
```

**Usage Example:**
```typescript
const newTrade = await tradesApi.create({
  symbol: "NIFTY 21900 CE",
  index: "NIFTY",
  qty: 50,
  entryPrice: 125.50,
  status: "ACTIVE"
});
```

---

#### Update Trade
```
PUT /trades/:id
```

**Usage Example:**
```typescript
const updated = await tradesApi.update(1, {
  status: "CLOSED",
  currentPrice: 150.00
});
```

---

#### Delete Trade
```
DELETE /trades/:id
```

**Usage Example:**
```typescript
await tradesApi.delete(1);
```

---

### Orders Endpoints

#### Get All Orders
```
GET /orderHistory
```

**Response:**
```json
[
  {
    "id": "ORD001",
    "symbol": "NIFTY 21900 CE",
    "orderType": "BUY",
    "qty": 50,
    "price": 125.50,
    "status": "COMPLETED",
    "timestamp": "2025-01-16T09:30:00Z",
    "executedPrice": 125.50,
    "executedQty": 50
  }
]
```

**Usage Example:**
```typescript
import { ordersApi } from '@/lib/api';

const orders = await ordersApi.getAll();
```

---

#### Get Order by ID
```
GET /orderHistory/:id
```

---

#### Create Order
```
POST /orderHistory
```

**Request Body:**
```json
{
  "symbol": "NIFTY 21900 CE",
  "orderType": "BUY",
  "qty": 50,
  "price": 125.50,
  "status": "PENDING"
}
```

---

#### Cancel Order
```
PATCH /orderHistory/:id
```

**Request Body:**
```json
{
  "status": "CANCELLED"
}
```

**Usage Example:**
```typescript
await ordersApi.cancel("ORD001");
```

---

### Strategies Endpoints

#### Get All Strategies
```
GET /strategies
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Straddle Strategy",
    "index": "NIFTY",
    "status": "ACTIVE",
    "description": "Long straddle on NIFTY index with CE and PE contracts",
    "entryDate": "2025-01-10T09:30:00Z",
    "profitTarget": 500,
    "stopLoss": 200,
    "currentPnl": 840,
    "trades": 12,
    "winRate": 75
  }
]
```

**Usage Example:**
```typescript
import { strategiesApi } from '@/lib/api';

const strategies = await strategiesApi.getAll();
```

---

#### Create Strategy
```
POST /strategies
```

**Request Body:**
```json
{
  "name": "New Strategy",
  "index": "NIFTY",
  "status": "ACTIVE",
  "description": "Strategy description",
  "profitTarget": 500,
  "stopLoss": 200
}
```

---

#### Update Strategy
```
PUT /strategies/:id
```

---

#### Delete Strategy
```
DELETE /strategies/:id
```

---

### Users Endpoints

#### Get All Users
```
GET /users
```

**Response:**
```json
[
  {
    "id": "admin-1",
    "email": "admin@example.com",
    "role": "admin",
    "name": "Admin User",
    "createdAt": "2025-01-01T10:00:00Z"
  }
]
```

**Usage Example:**
```typescript
import { usersApi } from '@/lib/api';

const users = await usersApi.getAll();
```

---

#### Create User
```
POST /users
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "secure_password",
  "name": "New User",
  "role": "user"
}
```

---

#### Update User
```
PUT /users/:id
```

---

#### Delete User
```
DELETE /users/:id
```

---

### Logs Endpoints

#### Get All Logs
```
GET /logs
```

**Response:**
```json
[
  {
    "id": 1,
    "timestamp": "2025-01-17T15:45:23Z",
    "level": "INFO",
    "message": "Strategy 'Straddle Strategy' executed 5 contracts",
    "category": "STRATEGY",
    "source": "AlgoEngine"
  },
  {
    "id": 2,
    "timestamp": "2025-01-17T15:44:10Z",
    "level": "WARNING",
    "message": "Stop loss triggered on BANKNIFTY trade",
    "category": "TRADE",
    "source": "RiskManager"
  }
]
```

**Usage Example:**
```typescript
import { logsApi } from '@/lib/api';

const logs = await logsApi.getAll();
```

---

#### Get Log by ID
```
GET /logs/:id
```

---

### Alerts Endpoints

#### Get All Alerts
```
GET /alerts
```

**Response:**
```json
[
  {
    "id": 1,
    "message": "Order filled: NIFTY 21900 CE",
    "time": "2 mins ago",
    "type": "success",
    "timestamp": "2025-01-17T15:43:00Z"
  }
]
```

**Usage Example:**
```typescript
import { alertsApi } from '@/lib/api';

const alerts = await alertsApi.getAll();
```

---

### Analytics Endpoints

#### Get All Analytics
```
GET /analytics
```

**Response:**
```json
[
  {
    "id": 1,
    "date": "2025-01-17",
    "totalTrades": 15,
    "winningTrades": 11,
    "losingTrades": 4,
    "winRate": 73.3,
    "totalPnl": 2082,
    "averageWin": 189.27,
    "averageLoss": 120.5,
    "profitFactor": 1.57
  }
]
```

**Usage Example:**
```typescript
import { analyticsApi } from '@/lib/api';

const analytics = await analyticsApi.getAll();
```

---

#### Get Analytics by Date
```
GET /analytics?date=2025-01-17
```

---

## Error Handling

### Global Error Handler
The API client includes a global error handler that catches and standardizes all errors:

```typescript
try {
  const data = await tradesApi.getAll();
} catch (error: any) {
  console.error(error.message); // "API Error [500]: Server error"
  console.error(error.status);  // 500
  console.error(error.data);    // Additional error data
}
```

### Auto Logout on 401
If a 401 (Unauthorized) response is received, the app will automatically:
1. Clear the auth token from localStorage
2. Clear the user role from localStorage
3. Redirect to the login page

---

## Request/Response Interceptors

### Request Interceptor
- Automatically adds `Authorization` header if token exists
- Sets `Content-Type: application/json`
- Timeout: 10 seconds

### Response Interceptor
- Handles 401 responses with automatic logout
- Standardizes error responses
- Logs errors to console in development

---

## Usage Examples

### Example 1: Fetch Trades on Component Mount
```typescript
import { useEffect, useState } from 'react';
import { tradesApi } from '@/lib/api';

export const LiveTrades = () => {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTrades = async () => {
      try {
        setLoading(true);
        const data = await tradesApi.getAll();
        setTrades(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTrades();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {trades.map((trade) => (
        <div key={trade.id}>{trade.symbol}</div>
      ))}
    </div>
  );
};
```

---

### Example 2: Create New Order
```typescript
import { ordersApi } from '@/lib/api';

const createOrder = async () => {
  try {
    const newOrder = await ordersApi.create({
      symbol: "NIFTY 22000 CE",
      orderType: "BUY",
      qty: 100,
      price: 150.00,
      status: "PENDING"
    });
    console.log("Order created:", newOrder);
  } catch (error: any) {
    console.error("Failed to create order:", error.message);
  }
};
```

---

### Example 3: Real-time Data Updates
```typescript
import { useEffect, useState } from 'react';
import { marketApi } from '@/lib/api';

export const Dashboard = () => {
  const [indices, setIndices] = useState([]);

  useEffect(() => {
    const fetchIndices = async () => {
      const data = await marketApi.getIndices();
      setIndices(data);
    };

    fetchIndices();

    // Poll every 5 seconds
    const interval = setInterval(fetchIndices, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      {indices.map((index) => (
        <div key={index.id}>
          <span>{index.name}</span>
          <span>{index.value}</span>
        </div>
      ))}
    </div>
  );
};
```

---

## Development Tips

### Query Parameters
Use standard query parameters for filtering:
```typescript
// Get analytics for specific date
const data = await analyticsApi.getByDate('2025-01-17');
// Request: GET /analytics?date=2025-01-17
```

### Pagination (Future Enhancement)
```typescript
// Example for future implementation
const trades = await apiClient.get('/trades?_page=1&_limit=10');
```

### Sorting (JSON Server Features)
```typescript
// Example: Sort trades by creation date
const trades = await apiClient.get('/trades?_sort=createdAt&_order=desc');
```

---

## Troubleshooting

### API Server Not Starting
```bash
# Check if port 3001 is already in use
# Kill process on port 3001 and restart
npm run dev:api
```

### CORS Issues
The JSON Server running locally should not have CORS issues. If you encounter them:
- Ensure both servers are running
- Check that VITE_API_URL matches the JSON Server URL

### 401 Unauthorized
- Check if the token is stored in localStorage
- Verify the token hasn't expired
- Re-login and try again

---

## Future Enhancements

- [ ] Add JWT token refresh mechanism
- [ ] Implement request caching
- [ ] Add request retry logic
- [ ] Implement real-time WebSocket support
- [ ] Add TypeScript interfaces for all responses
- [ ] Implement request validation with Zod

---

## Support

For questions or issues with the API, please refer to:
- **API Client:** `src/lib/api.ts`
- **Database:** `db.json`
- **Environment:** `.env.local`

