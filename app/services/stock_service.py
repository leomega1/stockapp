import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
import logging
import os
import time

from app.models import Stock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Alpha Vantage API
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'


def get_sp500_tickers() -> List[str]:
    """
    Get S&P 500 ticker symbols (using a curated list)
    """
    # Alpha Vantage doesn't have an S&P 500 list endpoint, so we use a curated list
    return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 
            'UNH', 'JNJ', 'JPM', 'V', 'PG', 'XOM', 'HD', 'CVX', 'MA', 'BAC',
            'ABBV', 'PFE', 'COST', 'KO', 'AVGO', 'MRK', 'PEP', 'TMO', 'WMT',
            'CSCO', 'MCD', 'ABT', 'DHR', 'ACN', 'LIN', 'VZ', 'ADBE', 'NKE',
            'CRM', 'TXN', 'NEE', 'CMCSA', 'PM', 'DIS', 'ORCL', 'WFC', 'UPS',
            'INTC', 'AMD', 'QCOM', 'NFLX', 'HON']


def fetch_stock_data(ticker: str) -> Dict:
    """
    Fetch stock data for a single ticker using Alpha Vantage API
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dictionary with stock data
    """
    try:
        # Rate limiting - Alpha Vantage free tier: 5 calls/minute
        time.sleep(12)  # 12 seconds = 5 calls per minute max
        
        # Get daily time series
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': ticker,
            'apikey': ALPHA_VANTAGE_API_KEY,
            'outputsize': 'compact'
        }
        
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for API errors
        if 'Error Message' in data:
            logger.warning(f"API error for {ticker}: {data['Error Message']}")
            return None
        
        if 'Note' in data:
            logger.warning(f"Rate limit hit for {ticker}")
            return None
            
        if 'Time Series (Daily)' not in data:
            logger.warning(f"No time series data for {ticker}")
            return None
        
        time_series = data['Time Series (Daily)']
        dates = sorted(time_series.keys(), reverse=True)
        
        if len(dates) < 2:
            logger.warning(f"Insufficient data for {ticker}")
            return None
        
        # Get latest and previous day
        latest_date = dates[0]
        previous_date = dates[1]
        
        latest = time_series[latest_date]
        previous = time_series[previous_date]
        
        latest_close = float(latest['4. close'])
        previous_close = float(previous['4. close'])
        
        price_change = latest_close - previous_close
        price_change_pct = (price_change / previous_close) * 100
        
        return {
            'symbol': ticker,
            'name': ticker,  # Alpha Vantage free tier doesn't include company names easily
            'price': latest_close,
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'volume': int(latest['5. volume']),
            'date': datetime.strptime(latest_date, '%Y-%m-%d')
        }
    except Exception as e:
        logger.warning(f"Error fetching data for {ticker}: {str(e)[:100]}")
        return None


def get_daily_movers(db: Session, top_n: int = 5) -> Tuple[List[Stock], List[Stock]]:
    """
    Fetch and analyze S&P 500 stocks to find biggest winners and losers
    
    Args:
        db: Database session
        top_n: Number of top winners/losers to return
    
    Returns:
        Tuple of (winners, losers) as Stock objects
    """
    logger.info("Starting daily movers analysis...")
    
    tickers = get_sp500_tickers()
    
    # Alpha Vantage free tier: 5 calls/minute, 500 calls/day
    # For demo, we'll fetch 10 stocks (takes ~2 minutes)
    tickers = tickers[:10]
    logger.info(f"Fetching data for {len(tickers)} stocks (Alpha Vantage rate limit: 5/min)...")
    
    stock_data = []
    
    # Fetch data for all tickers (with progress logging)
    for i, ticker in enumerate(tickers):
        logger.info(f"Fetching {i+1}/{len(tickers)}: {ticker}...")
        
        data = fetch_stock_data(ticker)
        if data:
            stock_data.append(data)
            logger.info(f"✓ {ticker}: {data['price_change_pct']:+.2f}%")
    
    logger.info(f"Successfully fetched data for {len(stock_data)} out of {len(tickers)} stocks")
    
    if not stock_data:
        logger.error("No stock data was fetched!")
        return [], []
    
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
        logger.info(f"Winner: {data['symbol']} ({data['name']}) +{data['price_change_pct']:.2f}%")
    
    for data in losers_data:
        stock = Stock(**data)
        db.add(stock)
        losers.append(stock)
        logger.info(f"Loser: {data['symbol']} ({data['name']}) {data['price_change_pct']:.2f}%")
    
    db.commit()
    
    logger.info(f"Saved {len(winners)} winners and {len(losers)} losers to database")
    
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

