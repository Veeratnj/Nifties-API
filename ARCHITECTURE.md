# Nifties API - Complete Architecture Documentation

## Overview
This is a production-ready RESTful API built with FastAPI for a trading platform managing options trading. The architecture follows clean code principles with modular, reusable components.

## Architecture

### Directory Structure
```
app/
├── __init__.py                 # Package initialization
├── main.py                     # Application entry point
├── constants/
│   ├── __init__.py
│   └── const.py               # Application constants
├── controllers/               # API route handlers
│   ├── __init__.py
│   ├── auth_controller.py     # Authentication endpoints
│   ├── market_controller.py   # Market data endpoints
│   ├── trade_controller.py    # Trade management endpoints
│   ├── order_controller.py    # Order management endpoints
│   ├── strategy_controller.py # Strategy endpoints
│   ├── user_controller.py     # User management endpoints
│   ├── analytics_controller.py# Analytics endpoints
│   └── health_controller.py   # Health check endpoints
├── services/                  # Business logic layer
│   ├── __init__.py
│   ├── market_services.py     # Market data operations
│   ├── trade_services.py      # Trade operations
│   ├── order_services.py      # Order operations
│   ├── strategy_services.py   # Strategy operations
│   ├── user_services.py       # User operations
│   └── analytics_services.py  # Analytics operations
├── models/                    # SQLAlchemy database models
│   ├── __init__.py
│   └── models.py              # All ORM models
├── schemas/                   # Pydantic validation schemas
│   ├── __init__.py
│   └── schema.py              # Request/response schemas
├── middleware/                # ASGI middleware
│   ├── __init__.py
│   └── middleware.py          # Logging, auth, error handling
├── db/                        # Database configuration
│   ├── __init__.py
│   └── db.py                  # Database setup & sessions
└── utils/                     # Utility functions
    ├── __init__.py
    └── security.py            # JWT & password utilities
```

## Key Features

### 1. Authentication & Authorization
- **JWT-based authentication** with token refresh
- **Role-based access control** (RBAC): Admin, Trader, User
- **Password hashing** using bcrypt
- **Automatic token validation** on protected endpoints
- **Custom dependency injection** for role checking

```python
# Usage in endpoints
@router.post("/orders")
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),  # Required auth
    db: Session = Depends(get_db)
):
    # Endpoint logic
```

### 2. Database Models
Complete ORM models with relationships:
- **User**: Authentication & profile management
- **Trade**: Options trading records with PnL calculation
- **Order**: Buy/Sell order management
- **Strategy**: Trading strategies with performance tracking
- **MarketIndex**: Index tracking (NIFTY, BANKNIFTY, etc.)
- **PnL**: Profit/Loss records
- **Alert**: Notifications and alerts
- **Log**: System activity logging
- **Analytics**: Daily trading statistics

### 3. Pydantic Schemas
Type-safe request/response validation:
- **Enums** for status types (TradeStatus, OrderStatus, etc.)
- **Field validation** (min/max length, positive numbers)
- **Email validation** for user registration
- **Generic ResponseSchema** for consistent API responses
- **ErrorResponseSchema** for error handling

### 4. Service Layer
Reusable business logic:
- **MarketService**: Market data operations
- **TradeService**: Trade CRUD + PnL calculations
- **OrderService**: Order management with execution
- **StrategyService**: Strategy operations + performance tracking
- **UserService**: User management + authentication
- **AnalyticsService**: Trading analytics & statistics

Each service includes:
- Error handling with logging
- Database transaction management
- Business logic validation

### 5. Middleware
- **TimerMiddleware**: Request processing time tracking
- **LoggingMiddleware**: Structured request/response logging
- **AuthMiddleware**: Authentication logging
- **ErrorHandlingMiddleware**: Centralized error handling
- **CORSMiddleware**: Cross-origin resource sharing

### 6. Logging
Comprehensive logging system:
- **File-based logging** to `logs/app.log`
- **Console output** for development
- **Request tracking** with unique request IDs
- **Error tracking** with full stack traces
- **Structured format**: `[timestamp] - logger - level - message`

### 7. API Endpoints

#### Authentication
```
POST   /api/auth/login          # User login
POST   /api/auth/register       # User registration
POST   /api/auth/refresh        # Token refresh
```

#### Market Data
```
GET    /api/market/indices      # Get all market indices
GET    /api/market/indices/{name}
POST   /api/market/indices      # Create (Admin only)
PUT    /api/market/indices/{id} # Update (Admin only)
DELETE /api/market/indices/{id} # Delete (Admin only)

GET    /api/market/pnl          # Get all PnL records
GET    /api/market/pnl/{period}
POST   /api/market/pnl          # Create (Admin only)
```

#### Trades
```
GET    /api/trades              # Get user's trades
GET    /api/trades/{id}         # Get specific trade
POST   /api/trades              # Create new trade
PUT    /api/trades/{id}         # Update trade
DELETE /api/trades/{id}         # Delete trade
GET    /api/trades/active/all   # Get active trades
POST   /api/trades/{id}/close   # Close trade
```

#### Orders
```
GET    /api/orders              # Get user's orders
GET    /api/orders/{id}         # Get specific order
POST   /api/orders              # Create new order
PUT    /api/orders/{id}         # Update order
PATCH  /api/orders/{id}/cancel  # Cancel order
DELETE /api/orders/{id}         # Delete order
```

#### Strategies
```
GET    /api/strategies          # Get user's strategies
GET    /api/strategies/{id}     # Get specific strategy
POST   /api/strategies          # Create new strategy
PUT    /api/strategies/{id}     # Update strategy
DELETE /api/strategies/{id}     # Delete strategy
GET    /api/strategies/active/all  # Get active strategies
```

#### Users
```
GET    /api/users/me            # Get current user profile
PUT    /api/users/me            # Update profile
GET    /api/users               # Get all users (Admin)
GET    /api/users/{id}          # Get specific user
DELETE /api/users/{id}          # Delete user (Admin)
POST   /api/users/{id}/activate # Activate user (Admin)
POST   /api/users/{id}/deactivate # Deactivate user (Admin)
```

#### Analytics
```
GET    /api/analytics                    # Get all analytics
GET    /api/analytics/date/{date}        # Get by date
POST   /api/analytics                    # Create (Admin only)
GET    /api/analytics/range              # Get date range
GET    /api/analytics/latest/{days}      # Get latest N days
```

#### Health
```
GET    /api/health              # Health check
GET    /api/                    # Root endpoint
```

## Response Format

### Success Response
```json
{
  "data": [...],
  "status": 200,
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "message": "Error description",
  "status": 400,
  "data": null,
  "details": "Additional error details"
}
```

## Authentication

### Login Flow
1. User sends credentials to `/api/auth/login`
2. Server validates credentials and creates JWT token
3. Client stores token in localStorage as `af_token`
4. Client includes token in Authorization header: `Bearer {token}`
5. Server validates token on each request

### Token Payload
```json
{
  "sub": 1,              // User ID
  "email": "user@example.com",
  "role": "trader",      // admin, trader, user
  "exp": 1234567890     // Expiration time
}
```

## Running the Application

### Installation
```bash
pip install -r requirements.txt
```

### Environment Setup
Create `.env` file:
```
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./app/db/nifties.db
CORS_ORIGINS=*
```

### Start Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Code Quality Features

### Error Handling
- Custom exceptions with HTTP status codes
- Centralized error handling middleware
- Detailed error logging
- User-friendly error messages

### Input Validation
- Pydantic schema validation
- Field constraints (min/max, patterns)
- Email validation
- Enum validation for status types

### Security
- Password hashing with bcrypt
- JWT token-based auth
- Role-based access control
- Protected endpoints requiring authentication

### Logging
- Structured logging with timestamps
- Request ID tracking
- Performance metrics (processing time)
- Error stack traces

## Dependencies

```
fastapi==0.104.1           # Web framework
uvicorn==0.24.0            # ASGI server
sqlalchemy==2.0.23         # ORM
pydantic==2.5.0            # Data validation
passlib==1.7.4             # Password hashing
python-jose==3.3.0         # JWT handling
PyJWT==2.8.1               # JWT encoding/decoding
python-dotenv==1.0.0       # Environment variables
```

## Best Practices Implemented

1. **Separation of Concerns**: Controllers, Services, Models, Schemas
2. **DRY Principle**: Reusable services and utilities
3. **Type Safety**: Full type hints and Pydantic validation
4. **Error Handling**: Comprehensive try-except with logging
5. **Security**: JWT auth, password hashing, RBAC
6. **Logging**: Structured logging throughout the application
7. **Documentation**: Clear docstrings and comments
8. **Modularity**: Package-based structure with `__init__.py` files
9. **Consistency**: Standard response format across all endpoints
10. **Extensibility**: Easy to add new models, services, and endpoints

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Request rate limiting
- [ ] API versioning (v1, v2, etc.)
- [ ] Advanced filtering and pagination
- [ ] Caching layer (Redis)
- [ ] Database migrations (Alembic)
- [ ] Unit and integration tests
- [ ] API key authentication
- [ ] Audit logging
- [ ] Performance monitoring

## Contributing

When adding new features:
1. Create models in `models/models.py`
2. Create schemas in `schemas/schema.py`
3. Create service in `services/`
4. Create controller in `controllers/`
5. Include proper logging and error handling
6. Follow existing code patterns and conventions
