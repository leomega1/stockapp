# 📈 S&P 500 Stock Tracker with AI-Generated Articles

A full-stack application that automatically tracks the S&P 500's daily winners and losers and generates AI-powered articles explaining why each stock moved.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Next.js](https://img.shields.io/badge/next.js-14-black.svg)

## 🌟 Features

- **Automated Daily Analysis**: Identifies top 5 winners and losers from S&P 500
- **AI-Generated Articles**: Uses Claude AI to create insightful articles explaining stock movements
- **News Aggregation**: Collects relevant news for each stock
- **Beautiful UI**: Modern, responsive dashboard with dark mode support
- **RESTful API**: Well-documented backend API
- **Scheduled Jobs**: Automatically runs daily after market close

## 🏗️ Architecture

```
stockapp/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── services/    # Core business logic
│   │   ├── routers/     # API endpoints
│   │   └── models.py    # Database models
│   └── requirements.txt
│
└── frontend/         # Next.js frontend
    ├── app/             # Pages and layouts
    ├── components/      # React components
    └── lib/             # API client
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Claude API key (from Anthropic)
- News API key (optional, from newsapi.org)

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. **Run the backend:**
```bash
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Run the frontend:**
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

### First-Time Setup

After both services are running, trigger the first data fetch:

```bash
curl -X POST http://localhost:8000/api/stocks/fetch-movers
```

This will:
1. Fetch S&P 500 stock data
2. Identify top movers
3. Collect news
4. Generate AI articles

Then visit `http://localhost:3000` to see the results!

## 📋 Environment Variables

### Backend (.env)

```bash
DATABASE_URL=sqlite:///./stockapp.db
ANTHROPIC_API_KEY=your_claude_api_key_here
NEWS_API_KEY=your_news_api_key_here  # Optional
SCHEDULER_ENABLED=true
ENVIRONMENT=development
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🔑 API Keys

### Required:
- **Anthropic Claude API**: Get from [console.anthropic.com](https://console.anthropic.com/)

### Optional:
- **News API**: Get from [newsapi.org](https://newsapi.org/) (free tier available)
  - Falls back to Yahoo Finance news if not provided

## 📚 API Endpoints

### Stocks
- `GET /api/stocks/daily` - Get today's winners and losers
- `GET /api/stocks/{symbol}` - Get specific stock details
- `POST /api/stocks/fetch-movers` - Manually trigger data fetch

### Articles
- `GET /api/articles/daily` - Get today's articles
- `GET /api/articles/{id}` - Get specific article
- `GET /api/articles/stock/{symbol}` - Get articles for a stock
- `GET /api/articles/stock/{symbol}/news` - Get news for a stock

Full API documentation: `http://localhost:8000/docs`

## ⏰ Scheduler

The backend includes an automated scheduler that runs Monday-Friday at 4:30 PM ET (after market close) to:
1. Fetch all S&P 500 stock data
2. Identify top 5 winners and losers
3. Collect relevant news for each
4. Generate AI articles

To disable: Set `SCHEDULER_ENABLED=false` in backend `.env`

## 🎨 Screenshots

### Dashboard
- Displays top winners and losers
- Color-coded cards (green/red)
- Click to read full articles

### Article Page
- AI-generated explanation
- Stock performance data
- Related news headlines
- Professional, journalistic writing

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database
- **yfinance** - Stock data fetching
- **Anthropic Claude** - AI article generation
- **APScheduler** - Job scheduling
- **SQLite/PostgreSQL** - Database

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **React Query** - Data fetching
- **Recharts** - Charts and visualizations

## 🚢 Deployment

### Backend
- **Recommended**: Railway, Render, or DigitalOcean
- Supports both SQLite and PostgreSQL
- Set environment variables in hosting platform

### Frontend
- **Recommended**: Vercel (optimal for Next.js)
- Set `NEXT_PUBLIC_API_URL` to your backend URL
- Automatic deployments from GitHub

## 🧪 Development Tips

### Testing the Workflow

Manually trigger the daily job:
```bash
curl -X POST http://localhost:8000/api/stocks/fetch-movers
```

### View API Logs

Backend logs show detailed progress:
- Stock fetching progress
- News collection
- Article generation status

### Database

Default: SQLite (`stockapp.db`)

To use PostgreSQL:
1. Install PostgreSQL
2. Create database
3. Update `DATABASE_URL` in `.env`

## 📝 How It Works

1. **Data Collection**: Fetches daily price data for all S&P 500 stocks
2. **Analysis**: Calculates percentage changes and identifies top movers
3. **News Gathering**: Collects recent news articles for each stock
4. **AI Generation**: Claude analyzes the data and news to write explanatory articles
5. **Display**: Frontend shows results in an intuitive, beautiful interface

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional data sources
- More technical indicators
- Historical analysis features
- User accounts and favorites
- Email notifications

## ⚠️ Disclaimer

This application provides AI-generated analysis for educational purposes only. It should not be considered financial or investment advice. Always conduct your own research and consult with financial professionals before making investment decisions.

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🙏 Acknowledgments

- Data from Yahoo Finance
- News from News API and Yahoo Finance
- AI articles powered by Anthropic Claude
- S&P 500 ticker list from Wikipedia

## 📞 Support

For issues or questions:
1. Check the README files in `backend/` and `frontend/` directories
2. Review API documentation at `/docs`
3. Check logs for error messages

---

Built with ❤️ for investors who want to understand market movements

