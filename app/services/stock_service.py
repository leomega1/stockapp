import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
import logging

from app.models import Stock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_sp500_tickers() -> List[str]:
    """
    Fetch S&P 500 ticker symbols from Wikipedia
    """
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        sp500_table = tables[0]
        tickers = sp500_table['Symbol'].tolist()
        # Replace dots with dashes for Yahoo Finance compatibility
        tickers = [ticker.replace('.', '-') for ticker in tickers]
        logger.info(f"Fetched {len(tickers)} S&P 500 tickers")
        return tickers
    except Exception as e:
        logger.error(f"Error fetching S&P 500 tickers: {e}")
        # Return a subset of popular tickers as fallback
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 
                'UNH', 'JNJ', 'JPM', 'V', 'PG', 'XOM', 'HD', 'CVX', 'MA', 'BAC',
                'ABBV', 'PFE', 'COST', 'KO', 'AVGO', 'MRK', 'PEP', 'TMO', 'WMT',
                'CSCO', 'MCD', 'ABT', 'DHR', 'ACN', 'LIN', 'VZ', 'ADBE', 'NKE',
                'CRM', 'TXN', 'NEE', 'CMCSA', 'PM', 'DIS', 'ORCL', 'WFC', 'UPS']


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
    Fetch and analyze S&P 500 stocks to find biggest winners and losers
    
    Args:
        db: Database session
        top_n: Number of top winners/losers to return
    
    Returns:
        Tuple of (winners, losers) as Stock objects
    """
    logger.info("Starting daily movers analysis...")
    
    tickers = get_sp500_tickers()
    stock_data = []
    
    # Fetch data for all tickers (with progress logging)
    for i, ticker in enumerate(tickers):
        if i % 50 == 0:
            logger.info(f"Processed {i}/{len(tickers)} stocks...")
        
        data = fetch_stock_data(ticker)
        if data:
            stock_data.append(data)
    
    logger.info(f"Successfully fetched data for {len(stock_data)} stocks")
    
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

