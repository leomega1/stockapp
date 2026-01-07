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

