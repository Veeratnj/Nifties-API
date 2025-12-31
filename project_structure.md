# Project Structure

This file provides a tree view of the `app/` directory and its core components.

```text
app/
├── constants/
│   ├── __init__.py
│   ├── broker_constants.py
│   └── const.py
├── controllers/
│   ├── __init__.py
│   ├── alert_controller.py
│   ├── analytics_controller.py
│   ├── auth_controller.py
│   ├── chat_controller.py
│   ├── common.py
│   ├── health_controller.py
│   ├── log_controller.py
│   ├── market_controller.py
│   ├── nifties_opt_controller.py
│   ├── order_controller.py
│   ├── signal_controller.py
│   ├── strategy_controller.py
│   ├── tick_controller.py
│   ├── trade_controller.py
│   └── user_controller.py
├── db/
│   ├── __init__.py
│   └── db.py
├── middleware/
│   ├── __init__.py
│   └── middleware.py
├── models/
│   ├── __init__.py
│   └── models.py
├── schemas/
│   ├── __init__.py
│   ├── schema.py
│   └── signal_schema.py
├── services/
│   ├── __init__.py
│   ├── agents.py
│   ├── alert_services.py
│   ├── analytics_services.py
│   ├── broker_services.py
│   ├── chat_services.py
│   ├── common_services.py
│   ├── enhanced_signal_services.py
│   ├── log_services.py
│   ├── market_services.py
│   ├── order_service.py
│   ├── order_service_utils.py
│   ├── order_services.py
│   ├── position_service.py
│   ├── signal_service.py
│   ├── strategy_services.py
│   ├── tick_service.py
│   ├── trade_services.py
│   └── user_services.py
├── utils/
│   ├── __init__.py
│   └── security.py
├── __init__.py
└── main.py
```
