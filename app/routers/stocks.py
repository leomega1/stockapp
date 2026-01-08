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


@router.post("/add-test-data")
async def add_test_data(
    db: Session = Depends(get_db)
):
    """
    Add test data to see the app working
    """
    from datetime import datetime
    
    try:
        # Clear existing data
        db.query(Stock).delete()
        db.commit()
        
        # Add winners
        winners_data = [
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "price": 520.50, "price_change": 15.30, "price_change_pct": 3.03, "volume": 45000000, "date": datetime.now()},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "price": 380.25, "price_change": 8.50, "price_change_pct": 2.29, "volume": 28000000, "date": datetime.now()},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "price": 142.80, "price_change": 3.20, "price_change_pct": 2.29, "volume": 32000000, "date": datetime.now()},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "price": 178.90, "price_change": 3.40, "price_change_pct": 1.94, "volume": 41000000, "date": datetime.now()},
            {"symbol": "TSLA", "name": "Tesla Inc.", "price": 245.60, "price_change": 4.10, "price_change_pct": 1.70, "volume": 95000000, "date": datetime.now()},
        ]
        
        # Add losers
        losers_data = [
            {"symbol": "AAPL", "name": "Apple Inc.", "price": 185.50, "price_change": -3.80, "price_change_pct": -2.01, "volume": 52000000, "date": datetime.now()},
            {"symbol": "META", "name": "Meta Platforms Inc.", "price": 485.20, "price_change": -9.50, "price_change_pct": -1.92, "volume": 18000000, "date": datetime.now()},
            {"symbol": "UNH", "name": "UnitedHealth Group", "price": 520.30, "price_change": -8.70, "price_change_pct": -1.64, "volume": 3500000, "date": datetime.now()},
            {"symbol": "JNJ", "name": "Johnson & Johnson", "price": 158.90, "price_change": -2.10, "price_change_pct": -1.30, "volume": 7200000, "date": datetime.now()},
            {"symbol": "JPM", "name": "JPMorgan Chase", "price": 215.40, "price_change": -2.60, "price_change_pct": -1.19, "volume": 11000000, "date": datetime.now()},
        ]
        
        for data in winners_data + losers_data:
            stock = Stock(**data)
            db.add(stock)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Added 5 winners and 5 losers test data",
            "winners": [w["symbol"] for w in winners_data],
            "losers": [l["symbol"] for l in losers_data]
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

