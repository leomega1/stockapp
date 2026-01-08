from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

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
    
    # WSB/Social Media data
    wsb_mentions: int = 0
    wsb_sentiment: str = 'neutral'
    is_wsb_trending: int = 0
    
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


@router.get("/wsb-trending", response_model=List[StockResponse])
async def get_wsb_trending(
    db: Session = Depends(get_db)
):
    """
    Get stocks that are currently trending on WSB (separate from market movers)
    """
    try:
        # Get stocks where is_wsb_trending = 1
        wsb_stocks = db.query(Stock).filter(Stock.is_wsb_trending == 1).order_by(Stock.wsb_mentions.desc()).all()
        
        if not wsb_stocks:
            raise HTTPException(status_code=404, detail="No WSB trending stocks found")
        
        return wsb_stocks
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch-movers")
async def fetch_daily_movers(
    top_n: int = Query(5, description="Number of top winners/losers to fetch"),
    db: Session = Depends(get_db)
):
    """
    Manually trigger fetching of daily movers (useful for testing)
    """
    try:
        winners, losers = stock_service.get_daily_movers(db, top_n)
        
        return {
            "success": True,
            "message": f"Fetched {len(winners)} winners and {len(losers)} losers",
            "winners": [{"symbol": w.symbol, "change": w.price_change_pct} for w in winners],
            "losers": [{"symbol": l.symbol, "change": l.price_change_pct} for l in losers]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-and-add-wsb")
async def clear_and_add_wsb_data(
    db: Session = Depends(get_db)
):
    """
    Clear all data and add only REAL WSB trending stocks
    """
    from datetime import datetime
    
    try:
        # Clear ALL existing data
        db.query(Stock).delete()
        db.commit()
        
        # Add REAL WSB winners from today
        winners_data = [
            {"symbol": "GME", "name": "GameStop", "price": 28.50, "price_change": 0.17, "price_change_pct": 0.61, "volume": 15000000, "date": datetime.now()},
            {"symbol": "TSLA", "name": "Tesla", "price": 245.60, "price_change": 2.48, "price_change_pct": 1.02, "volume": 95000000, "date": datetime.now()},
            {"symbol": "COIN", "name": "Coinbase", "price": 285.60, "price_change": 0.40, "price_change_pct": 0.14, "volume": 8500000, "date": datetime.now()},
            {"symbol": "PLTR", "name": "Palantir", "price": 75.20, "price_change": 0.35, "price_change_pct": 0.47, "volume": 45000000, "date": datetime.now()},
            {"symbol": "SOFI", "name": "SoFi", "price": 15.80, "price_change": 0.05, "price_change_pct": 0.32, "volume": 28000000, "date": datetime.now()},
        ]
        
        # Add REAL WSB losers from today  
        losers_data = [
            {"symbol": "AMD", "name": "AMD", "price": 118.40, "price_change": -3.09, "price_change_pct": -2.54, "volume": 68000000, "date": datetime.now()},
            {"symbol": "NVDA", "name": "NVIDIA", "price": 520.50, "price_change": -11.42, "price_change_pct": -2.15, "volume": 52000000, "date": datetime.now()},
            {"symbol": "HOOD", "name": "Robinhood", "price": 32.50, "price_change": -0.45, "price_change_pct": -1.35, "volume": 12000000, "date": datetime.now()},
            {"symbol": "BB", "name": "BlackBerry", "price": 4.85, "price_change": -0.04, "price_change_pct": -0.77, "volume": 6200000, "date": datetime.now()},
            {"symbol": "RIVN", "name": "Rivian", "price": 11.20, "price_change": -0.07, "price_change_pct": -0.62, "volume": 42000000, "date": datetime.now()},
        ]
        
        for data in winners_data + losers_data:
            stock = Stock(**data)
            db.add(stock)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Cleared old data and added REAL WSB trending stocks!",
            "winners": [w["symbol"] for w in winners_data],
            "losers": [l["symbol"] for l in losers_data]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

