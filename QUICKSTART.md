# 🚀 Quick Start Guide

Get your S&P 500 Stock Tracker up and running in 5 minutes!

## Step 1: Get Your API Keys

### Required: Claude API Key
1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key (starts with `sk-ant-...`)

### Optional: News API Key
1. Go to [newsapi.org](https://newsapi.org/)
2. Sign up for free account
3. Copy your API key from dashboard
4. ⚠️ Not required - app will use Yahoo Finance news if omitted

## Step 2: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and add your Claude API key
# Use nano, vim, or any text editor
nano .env
```

In `.env`, set:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
NEWS_API_KEY=your-news-key-here  # Optional
```

```bash
# Start the backend
uvicorn app.main:app --reload
```

✅ Backend running at `http://localhost:8000`

## Step 3: Frontend Setup

Open a **new terminal window**:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start the frontend
npm run dev
```

✅ Frontend running at `http://localhost:3000`

## Step 4: Fetch Initial Data

Open a **third terminal window**:

```bash
# Trigger the first data fetch
curl -X POST http://localhost:8000/api/stocks/fetch-movers
```

This will:
- ⏳ Take 2-3 minutes (fetching 500+ stocks)
- 📊 Identify top 5 winners and losers
- 📰 Collect news for each
- 🤖 Generate AI articles

## Step 5: View the App

Open your browser and go to:
```
http://localhost:3000
```

You should see:
- ✅ Dashboard with winners and losers
- ✅ Green cards for winners, red for losers
- ✅ Click any card to read the AI-generated article

## Troubleshooting

### "No stock data found"
- Wait for the data fetch to complete (Step 4)
- Check backend logs for errors
- Verify API keys are correct in `.env`

### "API connection error"
- Make sure backend is running on port 8000
- Check that frontend `.env.local` has correct API URL
- Look for CORS errors in browser console

### "Article generation failed"
- Verify Claude API key is valid
- Check you have API credits remaining
- Backend will use fallback templates if API fails

### Backend won't start
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Windows: venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
npm run dev
```

## Daily Usage

After initial setup, the app will automatically:
- 📅 Run daily at 4:30 PM ET (after market close)
- 🔄 Fetch new data and generate articles
- 📧 Keep your dashboard up to date

To manually refresh:
```bash
curl -X POST http://localhost:8000/api/stocks/fetch-movers
```

## What's Next?

- 📖 Read the full [README.md](README.md)
- 🔧 Check out [backend/README.md](backend/README.md) for API details
- 🎨 Explore [frontend/README.md](frontend/README.md) for customization
- 🚀 Deploy to production (see main README)

## Need Help?

1. Check the main [README.md](README.md)
2. Review API docs at `http://localhost:8000/docs`
3. Look at backend logs for errors
4. Verify all dependencies are installed

---

Happy tracking! 📈

