# Stock Collector Platform

A full-stack financial data platform for real-time monitoring and analysis of stocks, ETFs, gold, silver, and other financial instruments.

## 🏗️ Architecture Overview

- **Backend**: Django REST API with PostgreSQL time-series optimization
- **Frontend**: React/TypeScript SPA with real-time WebSocket updates
- **Database**: PostgreSQL with separate tables for real-time (15s) and historical (daily) data
- **Authentication**: JWT-based user authentication
- **Real-time**: WebSocket connections for live financial data streaming

## 📁 Project Structure

```
stock-collector-platform/
├── backend/                    # Django REST API
│   ├── manage.py
│   ├── config/                # Django configuration
│   │   ├── settings/
│   │   │   ├── base.py        # Base settings
│   │   │   ├── development.py # Development settings
│   │   │   └── production.py  # Production settings
│   │   ├── urls.py            # Root URL configuration
│   │   ├── wsgi.py            # WSGI configuration
│   │   └── asgi.py            # ASGI configuration (WebSocket)
│   │
│   ├── apps/                  # Django applications
│   │   ├── core/              # Shared utilities
│   │   │   ├── models/        # Base model classes
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py    # Abstract base models
│   │   │   │   └── mixins.py  # Model mixins
│   │   │   ├── permissions.py # API permissions
│   │   │   ├── pagination.py  # Custom pagination
│   │   │   ├── websockets.py  # WebSocket consumers
│   │   │   └── utils.py       # Shared utilities
│   │   │
│   │   ├── users/             # User domain management
│   │   │   ├── models/        # User-related models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py    # Custom User model
│   │   │   │   └── profile.py # User profile model
│   │   │   ├── services/      # User business logic
│   │   │   │   ├── user_service.py    # User CRUD operations
│   │   │   │   └── auth_service.py    # Authentication logic
│   │   │   ├── serializers/   # User serializers
│   │   │   │   ├── user_serializers.py
│   │   │   │   └── auth_serializers.py
│   │   │   ├── views/         # Django Views
│   │   │   │   ├── user_views.py      # User CRUD views
│   │   │   │   └── auth_views.py      # Authentication views
│   │   │   └── permissions.py # Custom permissions
│   │   │
│   │   ├── financial_data/    # Financial instruments data
│   │   │   ├── models/
│   │   │   │   ├── base.py    # Base financial instrument
│   │   │   │   ├── realtime.py # Real-time data (15s updates)
│   │   │   │   └── historical.py # Historical data (daily)
│   │   │   ├── services/
│   │   │   │   ├── data_aggregation.py    # Daily aggregation
│   │   │   │   ├── realtime_updater.py    # Real-time updates
│   │   │   │   └── chart_data_service.py  # Chart data processing
│   │   │   ├── serializers/
│   │   │   │   ├── chart_serializers.py   # Chart data serializers
│   │   │   │   └── instrument_serializers.py # Instrument serializers
│   │   │   ├── views/
│   │   │   │   ├── api.py      # REST API endpoints
│   │   │   │   └── websocket.py # WebSocket views
│   │   │   ├── urls.py         # App URL configuration
│   │   │   └── admin.py        # Django admin
│   │   │
│   │   └── portfolio/         # User portfolio management
│   │       ├── models/        # Portfolio-related models
│   │       │   ├── __init__.py
│   │       │   ├── watchlist.py # User watchlists
│   │       │   └── portfolio.py # User portfolios
│   │       ├── serializers.py # Portfolio serializers
│   │       ├── views.py       # Portfolio API endpoints
│   │       └── urls.py        # Portfolio URLs
│   │
│   ├── requirements/          # Python dependencies
│   │   ├── base.txt           # Base requirements
│   │   ├── development.txt    # Development requirements
│   │   └── production.txt     # Production requirements
│   │
│   └── tests/                 # Backend tests
│       ├── test_models.py
│       ├── test_services.py
│       └── test_api.py
│
├── frontend/                  # React/TypeScript UI
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   │
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── common/        # Generic components
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   └── Modal.tsx
│   │   │   ├── charts/        # Chart components
│   │   │   │   ├── FinancialChart.tsx
│   │   │   │   ├── RealtimeChart.tsx
│   │   │   │   └── HistoricalChart.tsx
│   │   │   └── layout/        # Layout components
│   │   │       ├── Header.tsx
│   │   │       ├── Sidebar.tsx
│   │   │       └── Footer.tsx
│   │   │
│   │   ├── pages/             # Route components
│   │   │   ├── Dashboard.tsx  # Main dashboard
│   │   │   ├── Login.tsx      # Authentication
│   │   │   ├── Register.tsx   # User registration
│   │   │   ├── StockDetail.tsx # Individual stock view
│   │   │   ├── ETFDetail.tsx   # ETF detail view
│   │   │   ├── CommodityDetail.tsx # Gold/Silver view
│   │   │   └── Portfolio.tsx   # User portfolio
│   │   │
│   │   ├── services/          # API client services
│   │   │   ├── api.ts         # Base HTTP client setup
│   │   │   ├── auth.ts        # Authentication service
│   │   │   ├── websocket.ts   # WebSocket client
│   │   │   ├── financial-data.ts # Financial data API
│   │   │   └── portfolio.ts   # Portfolio API
│   │   │
│   │   ├── hooks/             # Custom React hooks
│   │   │   ├── useAuth.ts     # Authentication hook
│   │   │   ├── useWebSocket.ts # WebSocket hook
│   │   │   ├── useChartData.ts # Chart data hook
│   │   │   └── useLocalStorage.ts # Local storage hook
│   │   │
│   │   ├── store/             # State management
│   │   │   ├── auth.ts        # Authentication state
│   │   │   ├── financial-data.ts # Financial data state
│   │   │   └── portfolio.ts   # Portfolio state
│   │   │
│   │   ├── types/             # TypeScript definitions
│   │   │   ├── auth.ts        # Authentication types
│   │   │   ├── financial-data.ts # Financial data types
│   │   │   ├── portfolio.ts   # Portfolio types
│   │   │   └── api.ts         # API response types
│   │   │
│   │   ├── utils/             # Helper functions
│   │   │   ├── formatters.ts  # Data formatters
│   │   │   ├── validators.ts  # Form validators
│   │   │   ├── constants.ts   # App constants
│   │   │   └── helpers.ts     # General helpers
│   │   │
│   │   ├── styles/            # CSS/styling
│   │   │   ├── globals.css    # Global styles
│   │   │   └── components.css # Component styles
│   │   │
│   │   ├── App.tsx            # Main App component
│   │   ├── index.tsx          # App entry point
│   │   └── vite-env.d.ts      # Vite type definitions
│   │
│   ├── package.json           # Node.js dependencies
│   ├── tsconfig.json          # TypeScript configuration
│   ├── tailwind.config.js     # Tailwind CSS configuration
│   ├── vite.config.ts         # Vite configuration
│   └── .eslintrc.json         # ESLint configuration
│
├── docker/                    # Container configurations
│   ├── backend.Dockerfile     # Backend Docker image
│   ├── frontend.Dockerfile    # Frontend Docker image
│   ├── postgres.Dockerfile    # PostgreSQL with optimizations
│   └── docker-compose.yml     # Multi-container setup
│
├── docs/                      # Documentation
│   ├── api.md                 # API documentation
│   ├── database-schema.md     # Database design
│   ├── deployment.md          # Deployment guide
│   └── development.md         # Development setup
│
├── scripts/                   # Utility scripts
│   ├── setup.sh               # Project setup script
│   ├── migrate.sh             # Database migration script
│   └── deploy.sh              # Deployment script
│
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

### Django Views and Services Pattern

**Django's MVT Pattern:**
- **Models**: Data layer (database entities)
- **Views**: HTTP request/response handling
- **Templates**: Presentation layer (HTML rendering)

**Modern Django Architecture:**
```python
# Layered Architecture
HTTP Request → View → Service → Repository → Model → Database
                ↓
            Response ← Serializer ← Service ← Repository ← Model ← Database
```

## 🗄️ Database Design

### Time-Series Optimization Strategy

The platform uses a dual-table approach for optimal performance:

#### 1. Real-time Data Table (`financial_data_realtime`)
- **Update frequency**: Every 15 seconds
- **Data retention**: Last 24 hours only
- **Purpose**: Live price updates and intraday charts
- **Indexes**: Optimized for latest data queries

#### 2. Historical Data Table (`financial_data_historical`)
- **Update frequency**: Daily (end of trading day)
- **Data retention**: 5+ years
- **Purpose**: Long-term analysis and historical charts
- **Indexes**: Optimized for date range queries

### Supported Financial Instruments

- **Stocks**: Individual company shares
- **ETFs**: Exchange-traded funds
- **Commodities**: Gold, Silver, Oil, etc.
- **Cryptocurrencies**: Bitcoin, Ethereum, etc.
- **Indices**: Market indices and benchmarks

## ✨ Key Features

### 🔍 **Public Features**
- **SEO-friendly instrument pages**: `<url>.com/AAPL`, `<url>.com/GOLD`
- **Real-time charts**: 15-second updates with multiple timeframes (1D, 5D, 1W, 2W, 1M, 1Y, 5Y)
- **View comments**: Read community discussions on each instrument page
- **Browse instruments**: Explore all available financial instruments

### 🔐 **Authenticated User Features**
- **Comment participation**: Leave comments and like/unlike others' comments
- **Social engagement**: User reputation system based on comment interactions
- **Personal watchlists**: Create and manage watchlists without alerts
- **Portfolio tracking**: Track your investments and performance
- **Real-time data access**: Live price updates via WebSocket

### � **Premium User Features**
- **Price alerts**: Get notified when instruments reach target prices
- **Advanced alert types**: Price above/below, percentage change alerts
- **Email & push notifications**: Multi-channel alert delivery
- **Higher API limits**: Increased rate limits for data access
- **Priority support**: Premium customer support

### 📊 **Financial Instruments Supported**
- **Stocks**: Individual company shares (AAPL, GOOGL, TSLA, etc.)
- **ETFs**: Exchange-traded funds
- **Commodities**: Gold, Silver, Oil, and other precious metals
- **Cryptocurrencies**: Bitcoin, Ethereum, and major altcoins
- **Indices**: Market indices and benchmarks