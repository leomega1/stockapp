import requests
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
import logging
import os

from app.models import Stock
from app.services.trending_service import get_combined_trending_tickers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Alpha Vantage API key
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "340WIPMNM58GMXMZ")


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
    Fetch stock data for a single ticker using Alpha Vantage API
    
    Args:
        ticker: Stock ticker symbol
        period: Not used (kept for compatibility)
    
    Returns:
        Dictionary with stock data
    """
    try:
        # Alpha Vantage TIME_SERIES_DAILY endpoint
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check for errors
        if "Error Message" in data:
            logger.warning(f"Alpha Vantage error for {ticker}: {data['Error Message']}")
            return None
        
        if "Note" in data:
            logger.warning(f"Alpha Vantage rate limit hit: {data['Note']}")
            return None
            
        if "Time Series (Daily)" not in data:
            logger.warning(f"No daily data for {ticker}")
            return None
        
        time_series = data["Time Series (Daily)"]
        dates = sorted(time_series.keys(), reverse=True)
        
        if len(dates) < 2:
            logger.warning(f"Not enough data for {ticker}")
            return None
        
        # Get latest and previous day
        latest_date = dates[0]
        previous_date = dates[1]
        
        latest = time_series[latest_date]
        previous = time_series[previous_date]
        
        # Calculate price change
        close_price = float(latest['4. close'])
        previous_close = float(previous['4. close'])
        price_change = close_price - previous_close
        price_change_pct = (price_change / previous_close) * 100
        
        # Get company name (Alpha Vantage doesn't provide it in this endpoint, use ticker)
        company_name = ticker
        
        return {
            'symbol': ticker,
            'name': company_name,
            'price': close_price,
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'volume': int(latest['5. volume']),
            'date': datetime.strptime(latest_date, '%Y-%m-%d')
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching {ticker}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        return None


def get_market_cap(ticker: str) -> float:
    """
    Get market cap for a stock using Alpha Vantage OVERVIEW endpoint
    Returns market cap in millions
    """
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "OVERVIEW",
            "symbol": ticker,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        market_cap_str = data.get('MarketCapitalization', '0')
        if market_cap_str and market_cap_str != 'None':
            market_cap = float(market_cap_str) / 1_000_000  # Convert to millions
            return market_cap
        return 0
        
    except Exception as e:
        logger.warning(f"Could not get market cap for {ticker}: {e}")
        return 0


def fetch_market_top_movers() -> Dict:
    """
    Fetch REAL top gainers and losers from Alpha Vantage
    FILTERS OUT micro-caps (< $500M market cap)
    Returns dict with 'top_gainers' and 'top_losers' lists
    """
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TOP_GAINERS_LOSERS",
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if "top_gainers" in data and "top_losers" in data:
            # Filter out penny stocks/micro-caps
            MIN_MARKET_CAP = 500  # $500M minimum
            MIN_PRICE = 5.0  # $5 minimum price (quick filter before API call)
            
            filtered_gainers = []
            for stock in data['top_gainers']:
                try:
                    price = float(stock['price'])
                    # Quick filter: skip penny stocks (< $5)
                    if price < MIN_PRICE:
                        logger.debug(f"Skipping {stock['ticker']} - penny stock (${price})")
                        continue
                    
                    # Check market cap (this makes API call, so we limit checks)
                    if len(filtered_gainers) < 20:  # Only check first 20 to avoid rate limits
                        time.sleep(1)  # Rate limit protection
                        market_cap = get_market_cap(stock['ticker'])
                        if market_cap >= MIN_MARKET_CAP:
                            filtered_gainers.append(stock)
                            logger.info(f"✅ {stock['ticker']}: ${price}, Market Cap: ${market_cap:.0f}M")
                        else:
                            logger.info(f"❌ {stock['ticker']}: ${price}, Market Cap: ${market_cap:.0f}M - TOO SMALL")
                except Exception as e:
                    logger.error(f"Error filtering {stock.get('ticker', 'unknown')}: {e}")
            
            filtered_losers = []
            for stock in data['top_losers']:
                try:
                    price = float(stock['price'])
                    # Quick filter: skip penny stocks
                    if price < MIN_PRICE:
                        logger.debug(f"Skipping {stock['ticker']} - penny stock (${price})")
                        continue
                    
                    # Check market cap
                    if len(filtered_losers) < 20:
                        time.sleep(1)  # Rate limit protection
                        market_cap = get_market_cap(stock['ticker'])
                        if market_cap >= MIN_MARKET_CAP:
                            filtered_losers.append(stock)
                            logger.info(f"✅ {stock['ticker']}: ${price}, Market Cap: ${market_cap:.0f}M")
                        else:
                            logger.info(f"❌ {stock['ticker']}: ${price}, Market Cap: ${market_cap:.0f}M - TOO SMALL")
                except Exception as e:
                    logger.error(f"Error filtering {stock.get('ticker', 'unknown')}: {e}")
            
            logger.info(f"✅ After filtering: {len(filtered_gainers)} gainers, {len(filtered_losers)} losers (all > $500M market cap)")
            return {"top_gainers": filtered_gainers, "top_losers": filtered_losers}
        else:
            logger.warning("No top movers data in Alpha Vantage response")
            return {"top_gainers": [], "top_losers": []}
            
    except Exception as e:
        logger.error(f"Error fetching top movers: {e}")
        return {"top_gainers": [], "top_losers": []}


def get_daily_movers(db: Session, top_n: int = 5) -> Tuple[List[Stock], List[Stock]]:
    """
    Fetch REAL market top movers and mark which ones are trending on WSB
    HYBRID APPROACH: Shows actual biggest market movers + WSB trending indicators
    
    Args:
        db: Database session
        top_n: Number of top winners/losers to return
    
    Returns:
        Tuple of (winners, losers) as Stock objects
    """
    logger.info("🔥 Starting HYBRID analysis: Real market movers + WSB trending...")
    
    # Clear old data first to avoid duplicates
    db.query(Stock).delete()
    db.commit()
    logger.info("✅ Cleared old stock data")
    
    # Step 1: Get WSB trending tickers for cross-reference
    wsb_trending_data = get_combined_trending_tickers(limit=50)
    wsb_dict = {item['ticker']: item for item in wsb_trending_data}
    logger.info(f"📊 Got {len(wsb_dict)} WSB trending tickers for reference")
    
    # Step 2: Get REAL market top movers from Alpha Vantage
    market_data = fetch_market_top_movers()
    
    # Step 3: Process top gainers
    winners = []
    for item in market_data.get('top_gainers', [])[:top_n]:
        try:
            ticker = item['ticker']
            
            # Check if this stock is also trending on WSB
            is_wsb = ticker in wsb_dict
            wsb_info = wsb_dict.get(ticker, {})
            
            stock_data = {
                'symbol': ticker,
                'name': ticker,  # Alpha Vantage doesn't provide name in this endpoint
                'price': float(item['price']),
                'price_change': float(item['change_amount']),
                'price_change_pct': float(item['change_percentage'].replace('%', '')),
                'volume': int(item['volume']),
                'date': datetime.now(),
                'wsb_mentions': wsb_info.get('mentions', 0),
                'wsb_sentiment': wsb_info.get('sentiment', 'neutral'),
                'is_wsb_trending': 1 if is_wsb else 0
            }
            
            stock = Stock(**stock_data)
            db.add(stock)
            winners.append(stock)
            
            wsb_badge = "🔥 WSB TRENDING" if is_wsb else ""
            logger.info(f"🚀 Winner: {ticker} +{stock_data['price_change_pct']:.2f}% {wsb_badge}")
            
        except Exception as e:
            logger.error(f"Error processing gainer {item}: {e}")
    
    # Step 4: Process top losers
    losers = []
    for item in market_data.get('top_losers', [])[:top_n]:
        try:
            ticker = item['ticker']
            
            # Check if this stock is also trending on WSB
            is_wsb = ticker in wsb_dict
            wsb_info = wsb_dict.get(ticker, {})
            
            stock_data = {
                'symbol': ticker,
                'name': ticker,
                'price': float(item['price']),
                'price_change': float(item['change_amount']),
                'price_change_pct': float(item['change_percentage'].replace('%', '')),
                'volume': int(item['volume']),
                'date': datetime.now(),
                'wsb_mentions': wsb_info.get('mentions', 0),
                'wsb_sentiment': wsb_info.get('sentiment', 'neutral'),
                'is_wsb_trending': 1 if is_wsb else 0
            }
            
            stock = Stock(**stock_data)
            db.add(stock)
            losers.append(stock)
            
            wsb_badge = "🔥 WSB TRENDING" if is_wsb else ""
            logger.info(f"📉 Loser: {ticker} {stock_data['price_change_pct']:.2f}% {wsb_badge}")
            
        except Exception as e:
            logger.error(f"Error processing loser {item}: {e}")
    
    db.commit()
    
    wsb_count = sum(1 for s in winners + losers if s.is_wsb_trending)
    logger.info(f"✅ Saved {len(winners)} winners and {len(losers)} losers to database")
    logger.info(f"🔥 {wsb_count} of them are ALSO trending on WSB!")
    
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

