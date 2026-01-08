"""
Social Media Aggregator Service
Fetches mentions from X (Twitter), WSB Reddit, and other sources
"""
import requests
import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


def fetch_wsb_comments(symbol: str) -> List[Dict]:
    """
    Fetch WSB Reddit comments mentioning the stock
    Using pushshift.io or Reddit API (mock for now)
    """
    try:
        # TODO: Implement real Reddit API integration
        # For now, return structured mock data showing what we'd fetch
        mock_comments = [
            {
                'author': 'WSB User',
                'comment': f'{symbol} to the moon! 🚀 Market undervalued this gem',
                'upvotes': 450,
                'timestamp': datetime.now().isoformat(),
                'sentiment': 'bullish'
            },
            {
                'author': 'Diamond Hands',
                'comment': f'Been holding {symbol} for months. Finally paying off!',
                'upvotes': 320,
                'timestamp': datetime.now().isoformat(),
                'sentiment': 'bullish'
            },
            {
                'author': 'Technical Trader',
                'comment': f'{symbol} breaking key resistance levels. Watch for continuation',
                'upvotes': 280,
                'timestamp': datetime.now().isoformat(),
                'sentiment': 'neutral'
            }
        ]
        
        logger.info(f"Fetched {len(mock_comments)} WSB comments for {symbol}")
        return mock_comments
        
    except Exception as e:
        logger.error(f"Error fetching WSB comments for {symbol}: {e}")
        return []


def fetch_twitter_mentions(symbol: str) -> List[Dict]:
    """
    Fetch X (Twitter) mentions from trusted accounts
    Would use Twitter API v2 (requires paid access)
    """
    try:
        # TODO: Implement real Twitter API integration
        # For now, return structured mock data from "trusted" accounts
        mock_tweets = [
            {
                'author': '@MarketAnalyst',
                'author_followers': 125000,
                'tweet': f'Significant volume surge in ${symbol}. Institutional interest appears strong',
                'likes': 1200,
                'retweets': 450,
                'timestamp': datetime.now().isoformat(),
                'verified': True
            },
            {
                'author': '@StockInsights',
                'author_followers': 89000,
                'tweet': f'${symbol} breaking out on technical charts. Key support at current levels',
                'likes': 890,
                'retweets': 320,
                'timestamp': datetime.now().isoformat(),
                'verified': True
            },
            {
                'author': '@FinanceNews',
                'author_followers': 250000,
                'tweet': f'${symbol} sees major price movement today. Analysts watching closely',
                'likes': 2100,
                'retweets': 780,
                'timestamp': datetime.now().isoformat(),
                'verified': True
            }
        ]
        
        logger.info(f"Fetched {len(mock_tweets)} Twitter mentions for {symbol}")
        return mock_tweets
        
    except Exception as e:
        logger.error(f"Error fetching Twitter mentions for {symbol}: {e}")
        return []


def get_comprehensive_social_context(symbol: str) -> Dict:
    """
    Aggregate all social media context for a stock
    Returns a structured dict with all sources
    """
    logger.info(f"Aggregating comprehensive social context for {symbol}")
    
    wsb_comments = fetch_wsb_comments(symbol)
    twitter_mentions = fetch_twitter_mentions(symbol)
    
    # Calculate sentiment aggregate
    total_mentions = len(wsb_comments) + len(twitter_mentions)
    
    bullish_count = sum(1 for c in wsb_comments if c.get('sentiment') == 'bullish')
    
    sentiment = 'bullish' if bullish_count > len(wsb_comments) / 2 else 'neutral'
    
    return {
        'total_mentions': total_mentions,
        'wsb_comments': wsb_comments,
        'twitter_mentions': twitter_mentions,
        'overall_sentiment': sentiment,
        'engagement': {
            'wsb_upvotes': sum(c.get('upvotes', 0) for c in wsb_comments),
            'twitter_likes': sum(t.get('likes', 0) for t in twitter_mentions),
            'twitter_retweets': sum(t.get('retweets', 0) for t in twitter_mentions)
        }
    }


def format_social_context_for_ai(social_data: Dict) -> str:
    """
    Format social media data into a readable string for Claude
    """
    lines = []
    
    lines.append(f"\n📊 SOCIAL MEDIA SENTIMENT ({social_data['total_mentions']} total mentions)")
    lines.append(f"Overall Sentiment: {social_data['overall_sentiment'].upper()}")
    lines.append(f"\n🔥 WALLSTREETBETS DISCUSSION:")
    
    for i, comment in enumerate(social_data['wsb_comments'][:3], 1):
        lines.append(f"{i}. [{comment['upvotes']} upvotes] {comment['comment']}")
    
    lines.append(f"\n🐦 TWITTER/X MENTIONS (From Verified/Trusted Accounts):")
    
    for i, tweet in enumerate(social_data['twitter_mentions'][:3], 1):
        followers = tweet['author_followers']
        lines.append(f"{i}. {tweet['author']} ({followers:,} followers):")
        lines.append(f"   \"{tweet['tweet']}\"")
        lines.append(f"   [{tweet['likes']} likes, {tweet['retweets']} retweets]")
    
    return "\n".join(lines)

