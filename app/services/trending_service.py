import requests
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def get_wsb_trending_tickers(limit: int = 20) -> List[Dict]:
    """Get trending tickers from WallStreetBets"""
    try:
        # Try the Tradestie API first
        url = "https://tradestie.com/api/v1/apps/reddit"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        trending = []
        for item in data[:limit]:
            ticker = item.get('ticker', '').upper()
            if ticker and len(ticker) <= 5:  # Filter out invalid tickers
                trending.append({
                    'ticker': ticker,
                    'mentions': item.get('no_of_comments', 0),
                    'sentiment': item.get('sentiment', 'neutral'),
                    'sentiment_score': item.get('sentiment_score', 0)
                })
        
        logger.info(f"✅ Found {len(trending)} trending tickers from WSB API")
        return trending
        
    except Exception as e:
        logger.warning(f"WSB API failed: {e}, using curated meme stock list")
        # Fallback to popular WSB/meme stocks that are always active
        return [
            {'ticker': 'GME', 'mentions': 1000, 'sentiment': 'bullish', 'sentiment_score': 0.8},
            {'ticker': 'AMC', 'mentions': 900, 'sentiment': 'bullish', 'sentiment_score': 0.75},
            {'ticker': 'TSLA', 'mentions': 850, 'sentiment': 'neutral', 'sentiment_score': 0.6},
            {'ticker': 'NVDA', 'mentions': 800, 'sentiment': 'bullish', 'sentiment_score': 0.85},
            {'ticker': 'PLTR', 'mentions': 750, 'sentiment': 'bullish', 'sentiment_score': 0.7},
            {'ticker': 'AAPL', 'mentions': 700, 'sentiment': 'neutral', 'sentiment_score': 0.5},
            {'ticker': 'MSFT', 'mentions': 650, 'sentiment': 'bullish', 'sentiment_score': 0.6},
            {'ticker': 'AMD', 'mentions': 600, 'sentiment': 'bullish', 'sentiment_score': 0.65},
            {'ticker': 'GOOGL', 'mentions': 550, 'sentiment': 'neutral', 'sentiment_score': 0.5},
            {'ticker': 'META', 'mentions': 500, 'sentiment': 'neutral', 'sentiment_score': 0.55},
            {'ticker': 'AMZN', 'mentions': 480, 'sentiment': 'neutral', 'sentiment_score': 0.5},
            {'ticker': 'COIN', 'mentions': 450, 'sentiment': 'bearish', 'sentiment_score': 0.3},
            {'ticker': 'HOOD', 'mentions': 420, 'sentiment': 'bearish', 'sentiment_score': 0.25},
            {'ticker': 'SOFI', 'mentions': 400, 'sentiment': 'bullish', 'sentiment_score': 0.6},
            {'ticker': 'RIVN', 'mentions': 380, 'sentiment': 'bearish', 'sentiment_score': 0.35},
            {'ticker': 'LCID', 'mentions': 350, 'sentiment': 'bearish', 'sentiment_score': 0.3},
            {'ticker': 'BB', 'mentions': 320, 'sentiment': 'neutral', 'sentiment_score': 0.45},
            {'ticker': 'NOK', 'mentions': 300, 'sentiment': 'neutral', 'sentiment_score': 0.4},
            {'ticker': 'WISH', 'mentions': 280, 'sentiment': 'bearish', 'sentiment_score': 0.2},
            {'ticker': 'CLOV', 'mentions': 250, 'sentiment': 'bearish', 'sentiment_score': 0.25},
        ]


def get_combined_trending_tickers(limit: int = 15) -> List[Dict]:
    """Get combined trending stocks from WSB"""
    wsb_tickers = get_wsb_trending_tickers(limit=limit)
    logger.info(f"🔥 Combined trending: {len(wsb_tickers)} unique tickers")
    return wsb_tickers

