import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict
import logging
from app.models import StockNews
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


def fetch_news_from_newsapi(symbol: str, company_name: str) -> List[Dict]:
    """
    Fetch news from NewsAPI.org
    
    Args:
        symbol: Stock ticker symbol
        company_name: Company name for search
    
    Returns:
        List of news articles
    """
    if not settings.news_api_key:
        logger.warning("NEWS_API_KEY not set, skipping NewsAPI")
        return []
    
    try:
        # Calculate date range (last 2 days)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=2)
        
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': f'{company_name} OR {symbol}',
            'from': from_date.strftime('%Y-%m-%d'),
            'to': to_date.strftime('%Y-%m-%d'),
            'language': 'en',
            'sortBy': 'relevancy',
            'pageSize': 5,
            'apiKey': settings.news_api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = []
        
        for article in data.get('articles', []):
            articles.append({
                'headline': article.get('title', ''),
                'url': article.get('url', ''),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'summary': article.get('description', ''),
                'published_at': article.get('publishedAt', '')
            })
        
        logger.info(f"Fetched {len(articles)} articles for {symbol} from NewsAPI")
        return articles
        
    except Exception as e:
        logger.error(f"Error fetching news from NewsAPI for {symbol}: {e}")
        return []


def fetch_news_from_yfinance(symbol: str) -> List[Dict]:
    """
    Fetch news from Yahoo Finance
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        List of news articles
    """
    try:
        import yfinance as yf
        
        stock = yf.Ticker(symbol)
        news = stock.news
        
        articles = []
        for item in news[:5]:  # Get top 5 news items
            articles.append({
                'headline': item.get('title', ''),
                'url': item.get('link', ''),
                'source': item.get('publisher', 'Yahoo Finance'),
                'summary': item.get('summary', ''),
                'published_at': datetime.fromtimestamp(item.get('providerPublishTime', 0)).isoformat()
            })
        
        logger.info(f"Fetched {len(articles)} articles for {symbol} from Yahoo Finance")
        return articles
        
    except Exception as e:
        logger.error(f"Error fetching news from Yahoo Finance for {symbol}: {e}")
        return []


def fetch_stock_news(db: Session, symbol: str, company_name: str) -> List[StockNews]:
    """
    Fetch and store news for a specific stock
    
    Args:
        db: Database session
        symbol: Stock ticker symbol
        company_name: Company name
    
    Returns:
        List of StockNews objects
    """
    logger.info(f"Fetching news for {symbol} ({company_name})")
    
    # Try multiple sources
    all_articles = []
    
    # Try Yahoo Finance first (free, no API key needed)
    yf_articles = fetch_news_from_yfinance(symbol)
    all_articles.extend(yf_articles)
    
    # Try NewsAPI if API key is available
    if settings.news_api_key:
        newsapi_articles = fetch_news_from_newsapi(symbol, company_name)
        all_articles.extend(newsapi_articles)
    
    # Remove duplicates based on headline
    seen_headlines = set()
    unique_articles = []
    for article in all_articles:
        headline = article.get('headline', '')
        if headline and headline not in seen_headlines:
            seen_headlines.add(headline)
            unique_articles.append(article)
    
    # Save to database
    news_objects = []
    for article in unique_articles[:10]:  # Limit to 10 articles per stock
        news = StockNews(
            stock_symbol=symbol,
            date=datetime.now(),
            headline=article.get('headline', ''),
            url=article.get('url', ''),
            source=article.get('source', ''),
            summary=article.get('summary', '')
        )
        db.add(news)
        news_objects.append(news)
    
    db.commit()
    
    logger.info(f"Saved {len(news_objects)} news articles for {symbol}")
    return news_objects


def get_news_for_stock(db: Session, symbol: str, date: datetime = None) -> List[StockNews]:
    """
    Get stored news for a specific stock
    
    Args:
        db: Database session
        symbol: Stock ticker symbol
        date: Optional date filter
    
    Returns:
        List of StockNews objects
    """
    query = db.query(StockNews).filter(StockNews.stock_symbol == symbol)
    
    if date:
        start_of_day = datetime(date.year, date.month, date.day)
        end_of_day = start_of_day + timedelta(days=1)
        query = query.filter(StockNews.date >= start_of_day, StockNews.date < end_of_day)
    
    return query.order_by(StockNews.created_at.desc()).all()


def get_news_summary_for_article(db: Session, symbol: str) -> str:
    """
    Get a formatted summary of news for AI article generation
    
    Args:
        db: Database session
        symbol: Stock ticker symbol
    
    Returns:
        Formatted string of news headlines
    """
    news_items = get_news_for_stock(db, symbol)
    
    if not news_items:
        return "No recent news available."
    
    summary_lines = []
    for i, news in enumerate(news_items[:5], 1):
        summary_lines.append(f"{i}. {news.headline} ({news.source})")
        if news.summary:
            summary_lines.append(f"   {news.summary[:150]}...")
    
    return "\n".join(summary_lines)

