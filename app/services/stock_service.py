import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
import logging
import os

from app.models import Stock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Financial Modeling Prep API
FMP_API_KEY = os.getenv('FMP_API_KEY', '')
FMP_BASE_URL = 'https://financialmodelingprep.com/api/v3'


def get_sp500_tickers() -> List[str]:
    """
    Fetch S&P 500 ticker symbols from FMP API
    """
    try:
        url = f'{FMP_BASE_URL}/sp500_constituent?apikey={FMP_API_KEY}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        tickers = [item['symbol'] for item in data]
        
        if tickers:
            logger.info(f"Fetched {len(tickers)} S&P 500 tickers from FMP")
            return tickers
    except Exception as e:
        logger.error(f"Error fetching S&P 500 tickers from FMP: {e}")
    
    # Fallback list
    logger.warning("Using fallback ticker list")
    return ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 
            'UNH', 'JNJ', 'JPM', 'V', 'PG', 'XOM', 'HD', 'CVX', 'MA', 'BAC',
            'ABBV', 'PFE', 'COST', 'KO', 'AVGO', 'MRK', 'PEP', 'TMO', 'WMT',
            'CSCO', 'MCD', 'ABT', 'DHR', 'ACN', 'LIN', 'VZ', 'ADBE', 'NKE',
            'CRM', 'TXN', 'NEE', 'CMCSA', 'PM', 'DIS', 'ORCL', 'WFC', 'UPS',
            'INTC', 'AMD', 'QCOM']


def fetch_stock_data(ticker: str) -> Dict:
    """
    Fetch stock data for a single ticker using FMP API
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dictionary with stock data
    """
    try:
        # Get historical prices (last 5 days)
        url = f'{FMP_BASE_URL}/historical-price-full/{ticker}?apikey={FMP_API_KEY}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'historical' not in data or len(data['historical']) < 2:
            logger.warning(f"Insufficient data for {ticker}")
            return None
        
        # Get latest and previous day
        historical = data['historical']
        latest = historical[0]
        previous = historical[1]
        
        price_change = latest['close'] - previous['close']
        price_change_pct = (price_change / previous['close']) * 100
        
        # Get company profile for name
        profile_url = f'{FMP_BASE_URL}/profile/{ticker}?apikey={FMP_API_KEY}'
        try:
            profile_response = requests.get(profile_url, timeout=5)
            profile_data = profile_response.json()
            company_name = profile_data[0]['companyName'] if profile_data else ticker
        except:
            company_name = ticker
        
        return {
            'symbol': ticker,
            'name': company_name,
            'price': float(latest['close']),
            'price_change': float(price_change),
            'price_change_pct': float(price_change_pct),
            'volume': int(latest['volume']),
            'date': datetime.strptime(latest['date'], '%Y-%m-%d')
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
    
    # Limit to first 50 tickers to avoid rate limiting
    # In production, you'd want to fetch all, but with proper rate limiting
    tickers = tickers[:50]
    logger.info(f"Fetching data for {len(tickers)} stocks...")
    
    stock_data = []
    
    # Fetch data for all tickers (with progress logging)
    for i, ticker in enumerate(tickers):
        if i % 10 == 0:
            logger.info(f"Processed {i}/{len(tickers)} stocks...")
        
        data = fetch_stock_data(ticker)
        if data:
            stock_data.append(data)
    
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

