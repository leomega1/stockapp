# Project Structure

Complete file structure of the S&P 500 Stock Tracker application.

```
stockapp/
│
├── README.md                    # Main project documentation
├── QUICKSTART.md                # Quick start guide
├── PROJECT_STRUCTURE.md         # This file
├── .gitignore                   # Git ignore rules
│
├── backend/                     # Python FastAPI Backend
│   ├── README.md                # Backend documentation
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment variables template
│   ├── .env                     # Your environment variables (gitignored)
│   ├── .gitignore               # Backend-specific ignores
│   │
│   └── app/                     # Application code
│       ├── __init__.py
│       ├── main.py              # FastAPI application entry point
│       ├── config.py            # Configuration management
│       ├── database.py          # Database connection and session
│       ├── models.py            # SQLAlchemy database models
│       │
│       ├── services/            # Business logic layer
│       │   ├── __init__.py
│       │   ├── stock_service.py    # Stock data fetching and analysis
│       │   ├── news_service.py     # News aggregation
│       │   ├── ai_service.py       # AI article generation (Claude)
│       │   └── scheduler.py        # Daily job scheduling
│       │
│       └── routers/             # API endpoints
│           ├── __init__.py
│           ├── stocks.py           # Stock-related endpoints
│           └── articles.py         # Article-related endpoints
│
└── frontend/                    # Next.js Frontend
    ├── README.md                # Frontend documentation
    ├── package.json             # Node.js dependencies
    ├── tsconfig.json            # TypeScript configuration
    ├── next.config.js           # Next.js configuration
    ├── tailwind.config.ts       # TailwindCSS configuration
    ├── postcss.config.js        # PostCSS configuration
    ├── .env.local               # Environment variables (gitignored)
    ├── .gitignore               # Frontend-specific ignores
    │
    ├── app/                     # Next.js App Router
    │   ├── layout.tsx              # Root layout with navigation
    │   ├── page.tsx                # Dashboard page (/)
    │   ├── providers.tsx           # React Query provider
    │   ├── globals.css             # Global styles
    │   │
    │   └── article/             # Article pages
    │       └── [symbol]/           # Dynamic route for stock symbols
    │           └── page.tsx        # Article detail page
    │
    ├── components/              # React components
    │   ├── StockCard.tsx           # Individual stock card
    │   ├── StockChart.tsx          # Price chart component
    │   ├── LoadingSpinner.tsx      # Loading state
    │   └── ErrorMessage.tsx        # Error display
    │
    └── lib/                     # Utilities
        └── api.ts                  # API client and types
```

## Key Files Explained

### Backend

**`app/main.py`**
- FastAPI application setup
- CORS configuration
- Router registration
- Database initialization
- Scheduler startup

**`app/models.py`**
- `Stock`: Stock price and volume data
- `Article`: AI-generated articles
- `StockNews`: News items for stocks

**`app/services/stock_service.py`**
- Fetches S&P 500 ticker list
- Gets daily price data via yfinance
- Identifies top winners and losers
- Stores data in database

**`app/services/news_service.py`**
- Fetches news from Yahoo Finance
- Fetches news from News API (optional)
- Removes duplicates
- Stores in database

**`app/services/ai_service.py`**
- Generates prompts for Claude
- Creates articles explaining movements
- Falls back to templates if API unavailable
- Stores articles in database

**`app/services/scheduler.py`**
- Background job scheduler
- Runs daily at 4:30 PM ET
- Orchestrates the full workflow
- Logging and error handling

**`app/routers/stocks.py`**
- GET /api/stocks/daily
- GET /api/stocks/history
- GET /api/stocks/{symbol}
- POST /api/stocks/fetch-movers

**`app/routers/articles.py`**
- GET /api/articles/daily
- GET /api/articles/{id}
- GET /api/articles/stock/{symbol}
- GET /api/articles/stock/{symbol}/news

### Frontend

**`app/page.tsx`** (Dashboard)
- Fetches daily movers from API
- Displays winners and losers
- Grid layout with StockCard components
- React Query for data management

**`app/article/[symbol]/page.tsx`**
- Dynamic route for stock symbols
- Fetches article and stock data
- Displays full article content
- Shows related news
- Includes disclaimer

**`components/StockCard.tsx`**
- Displays stock information
- Color-coded by type (winner/loser)
- Hover effects and animations
- Links to article page

**`components/StockChart.tsx`**
- Recharts integration
- Line chart for price history
- Responsive design
- Dark mode support

**`lib/api.ts`**
- API client class
- TypeScript interfaces
- All API calls centralized
- Environment-aware base URL

## Data Flow

```
User Opens App
    ↓
Frontend (Next.js)
    ↓
Fetches from API → Backend (FastAPI)
    ↓
Queries Database → SQLite/PostgreSQL
    ↓
Returns Data
    ↓
Frontend Displays

---

Daily Scheduler (4:30 PM ET)
    ↓
Fetch S&P 500 Data (yfinance)
    ↓
Identify Winners/Losers
    ↓
Fetch News (Yahoo Finance, News API)
    ↓
Generate Articles (Claude AI)
    ↓
Store in Database
    ↓
Ready for Next Day
```

## Database Schema

### Stock Table
- id (Primary Key)
- symbol (Indexed)
- name
- date (Indexed)
- price
- price_change
- price_change_pct
- volume
- created_at

### Article Table
- id (Primary Key)
- stock_symbol (Foreign Key, Indexed)
- date (Indexed)
- title
- content
- movement_type (winner/loser)
- created_at

### StockNews Table
- id (Primary Key)
- stock_symbol (Foreign Key, Indexed)
- date (Indexed)
- headline
- url
- source
- summary
- created_at

## Technologies Used

### Backend Stack
- Python 3.11+
- FastAPI (Web Framework)
- SQLAlchemy (ORM)
- yfinance (Stock Data)
- Anthropic Claude (AI)
- APScheduler (Scheduling)
- Uvicorn (ASGI Server)

### Frontend Stack
- Next.js 14 (React Framework)
- TypeScript (Type Safety)
- TailwindCSS (Styling)
- React Query (Data Fetching)
- Recharts (Visualizations)
- date-fns (Date Formatting)

## Environment Variables

### Backend (.env)
```
DATABASE_URL=sqlite:///./stockapp.db
ANTHROPIC_API_KEY=sk-ant-...
NEWS_API_KEY=...
SCHEDULER_ENABLED=true
ENVIRONMENT=development
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Port Configuration

- Backend: `8000`
- Frontend: `3000`

Both ports can be changed if needed:
- Backend: `uvicorn app.main:app --port 8001`
- Frontend: `npm run dev -- -p 3001`

