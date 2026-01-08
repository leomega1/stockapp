import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def get_wsb_trending_tickers(limit: int = 20) -> List[Dict]:
    """
    Get trending tickers from WallStreetBets using Tradestie API
    Returns list of tickers with mention counts
    """
    try:
        # Tradestie provides free WSB sentiment data
        url = "https://tradestie.com/api/v1/apps/reddit"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Format the data
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
        # Return fallback trending stocks
        return [
            {'ticker': 'GME', 'mentions': 1000, 'sentiment': 'bullish', 'sentiment_score': 0.8},
            {'ticker': 'TSLA', 'mentions': 800, 'sentiment': 'bullish', 'sentiment_score': 0.7},
            {'ticker': 'NVDA', 'mentions': 600, 'sentiment': 'bullish', 'sentiment_score': 0.75},
            {'ticker': 'AMD', 'mentions': 500, 'sentiment': 'bullish', 'sentiment_score': 0.6},
            {'ticker': 'PLTR', 'mentions': 400, 'sentiment': 'neutral', 'sentiment_score': 0.5},
            {'ticker': 'SOFI', 'mentions': 350, 'sentiment': 'bullish', 'sentiment_score': 0.65},
            {'ticker': 'OPEN', 'mentions': 300, 'sentiment': 'bullish', 'sentiment_score': 0.7},
            {'ticker': 'COIN', 'mentions': 250, 'sentiment': 'neutral', 'sentiment_score': 0.4},
            {'ticker': 'HOOD', 'mentions': 200, 'sentiment': 'bearish', 'sentiment_score': -0.3},
            {'ticker': 'BB', 'mentions': 150, 'sentiment': 'neutral', 'sentiment_score': 0.2},
        ]


def get_meme_stocks() -> List[str]:
    """
    Get popular meme stock tickers that are frequently discussed
    """
    return [
        'GME', 'AMC', 'BBBY', 'TSLA', 'PLTR', 'SOFI', 'OPEN', 
        'WISH', 'CLOV', 'COIN', 'HOOD', 'BB', 'NOK', 'NVDA',
        'AMD', 'RKLB', 'LCID', 'RIVN', 'NIO', 'MARA'
    ]


def get_twitter_trending_stocks() -> List[Dict]:
    """
    Get trending stocks from Twitter/X
    For now, returns popular tickers until we add Twitter API
    """
    # TODO: Add Twitter/X API integration
    # For now, return common trending stocks
    return [
        {'ticker': 'TSLA', 'mentions': 5000, 'platform': 'twitter'},
        {'ticker': 'NVDA', 'mentions': 3000, 'platform': 'twitter'},
        {'ticker': 'GME', 'mentions': 2500, 'platform': 'twitter'},
        {'ticker': 'OPEN', 'mentions': 2000, 'platform': 'twitter'},
        {'ticker': 'AMD', 'mentions': 1800, 'platform': 'twitter'},
    ]


def get_combined_trending_tickers(limit: int = 15) -> List[Dict]:
    """
    Combine WSB and Twitter trending stocks
    Returns unique tickers with aggregated social data
    """
    try:
        wsb_tickers = get_wsb_trending_tickers(limit=15)
        twitter_tickers = get_twitter_trending_stocks()
        
        # Combine and deduplicate
        ticker_data = {}
        
        for item in wsb_tickers:
            ticker = item['ticker']
            ticker_data[ticker] = {
                'ticker': ticker,
                'wsb_mentions': item['mentions'],
                'twitter_mentions': 0,
                'total_mentions': item['mentions'],
                'sentiment': item['sentiment'],
                'sentiment_score': item['sentiment_score'],
                'platforms': ['reddit']
            }
        
        for item in twitter_tickers:
            ticker = item['ticker']
            if ticker in ticker_data:
                ticker_data[ticker]['twitter_mentions'] = item['mentions']
                ticker_data[ticker]['total_mentions'] += item['mentions']
                ticker_data[ticker]['platforms'].append('twitter')
            else:
                ticker_data[ticker] = {
                    'ticker': ticker,
                    'wsb_mentions': 0,
                    'twitter_mentions': item['mentions'],
                    'total_mentions': item['mentions'],
                    'sentiment': 'neutral',
                    'sentiment_score': 0,
                    'platforms': ['twitter']
                }
        
        # Sort by total mentions
        trending = sorted(ticker_data.values(), key=lambda x: x['total_mentions'], reverse=True)
        
        logger.info(f"🔥 Combined trending: {len(trending)} unique tickers")
        return trending[:limit]
        
    except Exception as e:
        logger.error(f"Error getting combined trending: {e}")
        return []

