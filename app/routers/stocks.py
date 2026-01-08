from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import threading

from app.database import get_db
from app.models import Stock
from app.services import stock_service

router = APIRouter()


class StockResponse(BaseModel):
    id: int
    symbol: str
    name: str
    date: datetime
    price: float
    price_change: float
    price_change_pct: float
    volume: int
    
    class Config:
        from_attributes = True


class DailyMoversResponse(BaseModel):
    date: datetime
    winners: List[StockResponse]
    losers: List[StockResponse]


@router.get("/daily", response_model=DailyMoversResponse)
async def get_daily_movers(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get today's top winners and losers from the S&P 500
    """
    try:
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            target_date = datetime.now()
        
        stocks = stock_service.get_stocks_by_date(db, target_date)
        
        if not stocks:
            raise HTTPException(status_code=404, detail="No stock data found for this date")
        
        # Sort and get top 5 winners and losers
        sorted_stocks = sorted(stocks, key=lambda x: x.price_change_pct, reverse=True)
        winners = sorted_stocks[:5]
        losers = sorted_stocks[-5:][::-1]
        
        return {
            "date": target_date,
            "winners": winners,
            "losers": losers
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[StockResponse])
async def get_stock_history(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get all stock data for a specific date
    """
    try:
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            target_date = datetime.now()
        
        stocks = stock_service.get_stocks_by_date(db, target_date)
        
        if not stocks:
            raise HTTPException(status_code=404, detail="No stock data found for this date")
        
        return stocks
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}", response_model=StockResponse)
async def get_stock_by_symbol(
    symbol: str,
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get stock data for a specific symbol
    """
    try:
        target_date = None
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        
        stock = stock_service.get_stock_by_symbol(db, symbol.upper(), target_date)
        
        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
        
        return stock
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending_stocks():
    """
    Get trending stocks from WSB and Twitter
    """
    try:
        from app.services.trending_service import get_combined_trending_tickers
        
        trending = get_combined_trending_tickers(limit=15)
        
        return {
            "success": True,
            "count": len(trending),
            "trending": trending,
            "sources": ["reddit/wsb", "twitter/x"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-test-data")
async def add_test_data(
    db: Session = Depends(get_db)
):
    """
    Add VIRAL/TRENDING test data to see the app working
    """
    from datetime import datetime
    
    try:
        # Clear existing data
        db.query(Stock).delete()
        db.commit()
        
        # Add VIRAL WINNERS (WSB favorites)
        winners_data = [
            {"symbol": "GME", "name": "GameStop Corp.", "price": 25.80, "price_change": 3.50, "price_change_pct": 15.70, "volume": 85000000, "date": datetime.now()},
            {"symbol": "OPEN", "name": "Opendoor Technologies", "price": 2.15, "price_change": 0.25, "price_change_pct": 13.16, "volume": 42000000, "date": datetime.now()},
            {"symbol": "TSLA", "name": "Tesla Inc.", "price": 245.60, "price_change": 18.40, "price_change_pct": 8.10, "volume": 125000000, "date": datetime.now()},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "price": 520.50, "price_change": 28.30, "price_change_pct": 5.75, "volume": 65000000, "date": datetime.now()},
            {"symbol": "PLTR", "name": "Palantir Technologies", "price": 45.20, "price_change": 2.10, "price_change_pct": 4.87, "volume": 38000000, "date": datetime.now()},
        ]
        
        # Add VIRAL LOSERS
        losers_data = [
            {"symbol": "HOOD", "name": "Robinhood Markets", "price": 18.50, "price_change": -2.80, "price_change_pct": -13.15, "volume": 28000000, "date": datetime.now()},
            {"symbol": "COIN", "name": "Coinbase Global", "price": 145.20, "price_change": -12.50, "price_change_pct": -7.93, "volume": 15000000, "date": datetime.now()},
            {"symbol": "WISH", "name": "ContextLogic Inc.", "price": 0.85, "price_change": -0.08, "price_change_pct": -8.60, "volume": 12000000, "date": datetime.now()},
            {"symbol": "LCID", "name": "Lucid Group", "price": 2.45, "price_change": -0.15, "price_change_pct": -5.77, "volume": 35000000, "date": datetime.now()},
            {"symbol": "RIVN", "name": "Rivian Automotive", "price": 11.20, "price_change": -0.55, "price_change_pct": -4.68, "volume": 42000000, "date": datetime.now()},
        ]
        
        for data in winners_data + losers_data:
            stock = Stock(**data)
            db.add(stock)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Added 5 VIRAL winners and 5 VIRAL losers (WSB favorites!)",
            "winners": [w["symbol"] for w in winners_data],
            "losers": [l["symbol"] for l in losers_data],
            "note": "These are the stocks WSB is talking about!"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch-movers")
async def fetch_daily_movers(
    top_n: int = Query(5, description="Number of top winners/losers to fetch")
):
    """
    Manually trigger fetching of daily movers (runs in background due to API rate limits)
    """
    import asyncio
    import logging
    logger = logging.getLogger(__name__)
    
    async def fetch_in_background_async():
        try:
            await asyncio.sleep(0.1)  # Let the response return first
            from app.database import SessionLocal
            logger.info("Starting background stock fetch...")
            db = SessionLocal()
            try:
                winners, losers = stock_service.get_daily_movers(db, top_n)
                logger.info(f"✅ Background fetch completed: {len(winners)} winners, {len(losers)} losers")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"❌ Background fetch error: {e}")
    
    # Fire and forget - don't await
    asyncio.create_task(fetch_in_background_async())
    
    # Return immediately
    return {
        "success": True,
        "message": "Stock fetch started in background. Check back in ~2 minutes.",
        "status": "processing"
    }

