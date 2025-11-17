# Quick Start Guide - Nifties API

## Prerequisites
- Python 3.8+
- pip (Python package manager)

## Installation & Setup (5 minutes)

### Step 1: Install Dependencies
```bash
cd d:\POC\smartAPI\nifties\Nifties-API
pip install -r requirements.txt
```

### Step 2: Create Environment File
```bash
# Copy the example
copy .env.example .env

# Edit .env (optional - defaults are provided)
# Key settings:
# JWT_SECRET_KEY=your-secret-key
# DATABASE_URL=sqlite:///./app/db/nifties.db
```

### Step 3: Run the Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Access the API

**Swagger UI (Interactive Docs)**
```
http://localhost:8000/docs
```

**Alternative API Docs (ReDoc)**
```
http://localhost:8000/redoc
```

## First Steps - Test the API

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

### 2. Register a User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trader@example.com",
    "name": "John Trader",
    "password": "securepass123",
    "role": "trader"
  }'
```

### 3. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trader@example.com",
    "password": "securepass123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "trader@example.com",
    "name": "John Trader",
    "role": "trader",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 4. Use the Token
Save the `access_token` and use it in requests:

```bash
# Set your token
set TOKEN=your_access_token_here

# Create a trade
curl -X POST http://localhost:8000/api/trades \
  -H "Authorization: Bearer %TOKEN%" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NIFTY 21900 CE",
    "index": "NIFTY",
    "strike": 21900,
    "type": "CE",
    "qty": 50,
    "entry_price": 125.50,
    "current_price": 142.30,
    "status": "ACTIVE",
    "strategy": "Straddle Strategy"
  }'
```

### 5. Get Your Trades
```bash
curl -X GET http://localhost:8000/api/trades \
  -H "Authorization: Bearer %TOKEN%"
```

## Using Swagger UI (Easier Way)

1. Go to http://localhost:8000/docs
2. Click **"Authorize"** button in top right
3. Enter: `Bearer YOUR_ACCESS_TOKEN`
4. Try endpoints directly from the UI

## Common Endpoints Quick Reference

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `POST /api/auth/refresh` - Refresh token

### Market Data
- `GET /api/market/indices` - Get market indices
- `GET /api/market/pnl` - Get P&L data

### Trades
- `GET /api/trades` - Get your trades
- `POST /api/trades` - Create new trade
- `PUT /api/trades/{id}` - Update trade
- `DELETE /api/trades/{id}` - Delete trade
- `POST /api/trades/{id}/close` - Close trade

### Orders
- `GET /api/orders` - Get your orders
- `POST /api/orders` - Create new order
- `PATCH /api/orders/{id}/cancel` - Cancel order

### Strategies
- `GET /api/strategies` - Get your strategies
- `POST /api/strategies` - Create new strategy
- `GET /api/strategies/active/all` - Get active strategies

### Users
- `GET /api/users/me` - Get your profile
- `PUT /api/users/me` - Update your profile

### Analytics
- `GET /api/analytics` - Get analytics data
- `GET /api/analytics/date/{date}` - Get analytics for specific date

## Troubleshooting

### Port Already in Use
```bash
# Use different port
uvicorn app.main:app --port 8001
```

### Database Issues
```bash
# Delete the database and restart (creates new one)
del app/db/nifties.db
```

### Import Errors
```bash
# Ensure you're in the right directory
cd d:\POC\smartAPI\nifties\Nifties-API
```

### Authorization Errors
- Make sure token is valid and not expired
- Check token format: `Bearer <token>`
- Re-login if token expired

## Environment Variables

```env
# JWT
JWT_SECRET_KEY=your-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./app/db/nifties.db

# Logging
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=*

# API
DEBUG=True
```

## Project Structure Overview

```
app/
├── controllers/     # API routes
├── services/        # Business logic
├── models/          # Database models
├── schemas/         # Validation schemas
├── middleware/      # Request middleware
├── db/              # Database setup
├── utils/           # Utilities (auth, security)
└── constants/       # Constants & config
```

## Key Features Ready to Use

✅ **User Authentication** - Register & login with JWT
✅ **Trading Management** - Create, update, close trades
✅ **Order Management** - Place & cancel orders
✅ **Strategies** - Create and track strategies
✅ **Market Data** - Track indices and P&L
✅ **Analytics** - Daily trading statistics
✅ **User Management** - Profile, admin controls
✅ **Logging** - Complete request/error logging
✅ **Authorization** - Role-based access control

## Next Steps

1. **Test all endpoints** using Swagger UI
2. **Read ARCHITECTURE.md** for detailed information
3. **Explore the code** to understand the patterns
4. **Add features** following the existing patterns
5. **Deploy** to production (update SECRET_KEY!)

## Need Help?

- **API Docs**: http://localhost:8000/docs
- **Architecture Guide**: See ARCHITECTURE.md
- **Code Examples**: See IMPLEMENTATION_SUMMARY.md
- **Source**: Explore the `app/` folder

Happy Trading! 🚀
