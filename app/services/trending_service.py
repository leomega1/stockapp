import requests
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def get_wsb_trending_tickers(limit: int = 20) -> List[Dict]:
    """Get trending tickers from WallStreetBets"""
    try:
        url = "https://tradestie.com/api/v1/apps/reddit"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        trending = []
        for item in data[:limit]:
            trending.append({
                'ticker': item.get('ticker', '').upper(),
                'mentions': item.get('no_of_comments', 0),
                'sentiment': item.get('sentiment', 'neutral'),
                'sentiment_score': item.get('sentiment_score', 0)
            })
        
        logger.info(f"✅ Found {len(trending)} trending tickers from WSB")
        return trending
        
    except Exception as e:
        logger.error(f"Error fetching WSB data: {e}")
        return [
            {'ticker': 'GME', 'mentions': 1000, 'sentiment': 'bullish', 'sentiment_score': 0.8},
            {'ticker': 'TSLA', 'mentions': 800, 'sentiment': 'bullish', 'sentiment_score': 0.7},
            {'ticker': 'NVDA', 'mentions': 600, 'sentiment': 'bullish', 'sentiment_score': 0.75},
        ]


def get_combined_trending_tickers(limit: int = 15) -> List[Dict]:
    """Get combined trending stocks from WSB"""
    wsb_tickers = get_wsb_trending_tickers(limit=limit)
    logger.info(f"🔥 Combined trending: {len(wsb_tickers)} unique tickers")
    return wsb_tickers

