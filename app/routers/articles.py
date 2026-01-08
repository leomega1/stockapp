from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.database import get_db
from app.models import Article, Stock, StockNews

router = APIRouter()


class ArticleResponse(BaseModel):
    id: int
    stock_symbol: str
    date: datetime
    title: str
    content: str
    movement_type: str
    slug: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ArticleWithStockResponse(BaseModel):
    id: int
    stock_symbol: str
    date: datetime
    title: str
    content: str
    movement_type: str
    slug: Optional[str] = None
    created_at: datetime
    stock_name: Optional[str] = None
    stock_price: Optional[float] = None
    stock_change_pct: Optional[float] = None
    
    class Config:
        from_attributes = True


class NewsItemResponse(BaseModel):
    id: int
    headline: str
    url: Optional[str]
    source: Optional[str]
    summary: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/daily", response_model=List[ArticleWithStockResponse])
async def get_daily_articles(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get all articles for today (or a specific date)
    """
    try:
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            target_date = datetime.now()
        
        start_of_day = datetime(target_date.year, target_date.month, target_date.day)
        end_of_day = start_of_day + timedelta(days=1)
        
        articles = db.query(Article).filter(
            Article.date >= start_of_day,
            Article.date < end_of_day
        ).all()
        
        if not articles:
            raise HTTPException(status_code=404, detail="No articles found for this date")
        
        # Enrich with stock data
        enriched_articles = []
        for article in articles:
            stock = db.query(Stock).filter(
                Stock.symbol == article.stock_symbol,
                Stock.date >= start_of_day,
                Stock.date < end_of_day
            ).first()
            
            enriched = ArticleWithStockResponse(
                id=article.id,
                stock_symbol=article.stock_symbol,
                date=article.date,
                title=article.title,
                content=article.content,
                movement_type=article.movement_type,
                created_at=article.created_at,
                stock_name=stock.name if stock else None,
                stock_price=stock.price if stock else None,
                stock_change_pct=stock.price_change_pct if stock else None
            )
            enriched_articles.append(enriched)
        
        return enriched_articles
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/slug/{slug}", response_model=ArticleWithStockResponse)
async def get_article_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific article by its URL slug
    Example: /api/articles/slug/WhyDidGMEGoUp15PercentToday-Jan82026
    """
    try:
        article = db.query(Article).filter(Article.slug == slug).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Get stock data
        stock = db.query(Stock).filter(
            Stock.symbol == article.stock_symbol
        ).order_by(Stock.date.desc()).first()
        
        return ArticleWithStockResponse(
            id=article.id,
            stock_symbol=article.stock_symbol,
            date=article.date,
            title=article.title,
            content=article.content,
            movement_type=article.movement_type,
            slug=article.slug,
            created_at=article.created_at,
            stock_name=stock.name if stock else None,
            stock_price=stock.price if stock else None,
            stock_change_pct=stock.price_change_pct if stock else None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{article_id}", response_model=ArticleWithStockResponse)
async def get_article_by_id(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific article by ID
    """
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Get stock data
        stock = db.query(Stock).filter(
            Stock.symbol == article.stock_symbol
        ).order_by(Stock.date.desc()).first()
        
        return ArticleWithStockResponse(
            id=article.id,
            stock_symbol=article.stock_symbol,
            date=article.date,
            title=article.title,
            content=article.content,
            movement_type=article.movement_type,
            slug=article.slug,
            created_at=article.created_at,
            stock_name=stock.name if stock else None,
            stock_price=stock.price if stock else None,
            stock_change_pct=stock.price_change_pct if stock else None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock/{symbol}", response_model=List[ArticleResponse])
async def get_articles_by_symbol(
    symbol: str,
    limit: int = Query(10, description="Maximum number of articles to return"),
    db: Session = Depends(get_db)
):
    """
    Get all articles for a specific stock symbol
    """
    try:
        articles = db.query(Article).filter(
            Article.stock_symbol == symbol.upper()
        ).order_by(Article.date.desc()).limit(limit).all()
        
        if not articles:
            raise HTTPException(status_code=404, detail=f"No articles found for {symbol}")
        
        return articles
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock/{symbol}/news", response_model=List[NewsItemResponse])
async def get_stock_news(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Get news items for a specific stock
    """
    try:
        news_items = db.query(StockNews).filter(
            StockNews.stock_symbol == symbol.upper()
        ).order_by(StockNews.created_at.desc()).limit(10).all()
        
        if not news_items:
            raise HTTPException(status_code=404, detail=f"No news found for {symbol}")
        
        return news_items
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[ArticleResponse])
async def get_article_history(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get articles for a specific date
    """
    try:
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            target_date = datetime.now()
        
        start_of_day = datetime(target_date.year, target_date.month, target_date.day)
        end_of_day = start_of_day + timedelta(days=1)
        
        articles = db.query(Article).filter(
            Article.date >= start_of_day,
            Article.date < end_of_day
        ).order_by(Article.created_at.desc()).all()
        
        return articles
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

