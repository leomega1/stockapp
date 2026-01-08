import yfinance as yf
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
import logging

from app.models import Stock
from app.services.trending_service import get_combined_trending_tickers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_trending_tickers() -> List[str]:
    """
    Fetch LIVE trending tickers from WSB and Twitter
    """
    try:
        trending_data = get_combined_trending_tickers(limit=20)
        tickers = [item['ticker'] for item in trending_data if item['ticker']]
        logger.info(f"🔥 Fetched {len(tickers)} LIVE trending tickers from WSB")
        return tickers
    except Exception as e:
        logger.error(f"Error fetching trending tickers: {e}")
        # Fallback to popular meme stocks
        return ['GME', 'AMC', 'TSLA', 'NVDA', 'PLTR', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']


def fetch_stock_data(ticker: str, period: str = "5d") -> Dict:
    """
    Fetch stock data for a single ticker
    
    Args:
        ticker: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, etc.)
    
    Returns:
        Dictionary with stock data
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if len(hist) < 2:
            return None
            
        # Get the latest and previous day's data
        latest = hist.iloc[-1]
        previous = hist.iloc[-2]
        
        price_change = latest['Close'] - previous['Close']
        price_change_pct = (price_change / previous['Close']) * 100
        
        # Get company info
        info = stock.info
        company_name = info.get('longName', ticker)
        
        return {
            'symbol': ticker,
            'name': company_name,
            'price': float(latest['Close']),
            'price_change': float(price_change),
            'price_change_pct': float(price_change_pct),
            'volume': int(latest['Volume']),
            'date': latest.name.to_pydatetime()
        }
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        return None


def get_daily_movers(db: Session, top_n: int = 5) -> Tuple[List[Stock], List[Stock]]:
    """
    Fetch and analyze TRENDING WSB stocks to find biggest winners and losers
    
    Args:
        db: Database session
        top_n: Number of top winners/losers to return
    
    Returns:
        Tuple of (winners, losers) as Stock objects
    """
    logger.info("🔥 Starting LIVE trending stocks analysis from WSB...")
    
    # Clear old data first to avoid duplicates
    db.query(Stock).delete()
    db.commit()
    logger.info("✅ Cleared old stock data")
    
    # Get LIVE trending tickers from WSB
    tickers = get_trending_tickers()
    logger.info(f"📊 Analyzing {len(tickers)} trending stocks: {', '.join(tickers[:10])}...")
    
    stock_data = []
    
    # Fetch data for trending tickers
    for i, ticker in enumerate(tickers):
        logger.info(f"Fetching {i+1}/{len(tickers)}: {ticker}...")
        
        data = fetch_stock_data(ticker)
        if data:
            stock_data.append(data)
            logger.info(f"✓ {ticker}: {data['price_change_pct']:+.2f}%")
        else:
            logger.warning(f"✗ Failed to get data for {ticker}")
    
    logger.info(f"Successfully fetched data for {len(stock_data)} trending stocks")
    
    if len(stock_data) < top_n * 2:
        logger.warning(f"Only got {len(stock_data)} stocks, expected at least {top_n * 2}")
    
    # Sort by percentage change
    stock_data.sort(key=lambda x: x['price_change_pct'], reverse=True)
    
    # Get top winners and losers
    winners_data = stock_data[:top_n]
    losers_data = stock_data[-top_n:][::-1]  # Reverse to show biggest loser first
    
    # Save to database
    winners = []
    losers = []
    
    for data in winners_data:
        stock = Stock(**data)
        db.add(stock)
        winners.append(stock)
        logger.info(f"🚀 Winner: {data['symbol']} ({data['name']}) +{data['price_change_pct']:.2f}%")
    
    for data in losers_data:
        stock = Stock(**data)
        db.add(stock)
        losers.append(stock)
        logger.info(f"📉 Loser: {data['symbol']} ({data['name']}) {data['price_change_pct']:.2f}%")
    
    db.commit()
    
    logger.info(f"✅ Saved {len(winners)} winners and {len(losers)} losers to database")
    
    return winners, losers


def get_stock_by_symbol(db: Session, symbol: str, date: datetime = None) -> Stock:
    """
    Get stock data for a specific symbol and date
    """
    query = db.query(Stock).filter(Stock.symbol == symbol)
    
    if date:
        # Get stocks for the specific date
        start_of_day = datetime(date.year, date.month, date.day)
        end_of_day = start_of_day + timedelta(days=1)
        query = query.filter(Stock.date >= start_of_day, Stock.date < end_of_day)
    
    return query.order_by(Stock.date.desc()).first()


def get_stocks_by_date(db: Session, date: datetime = None) -> List[Stock]:
    """
    Get all stocks for a specific date
    """
    if not date:
        date = datetime.now()
    
    start_of_day = datetime(date.year, date.month, date.day)
    end_of_day = start_of_day + timedelta(days=1)
    
    return db.query(Stock).filter(
        Stock.date >= start_of_day,
        Stock.date < end_of_day
    ).order_by(Stock.price_change_pct.desc()).all()

