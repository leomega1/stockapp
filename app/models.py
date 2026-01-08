from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    name = Column(String)
    date = Column(DateTime, index=True)
    price = Column(Float)
    price_change = Column(Float)
    price_change_pct = Column(Float)
    volume = Column(Integer)
    
    # WSB/Social Media tracking
    wsb_mentions = Column(Integer, default=0)
    wsb_sentiment = Column(String, default='neutral')  # bullish/bearish/neutral
    is_wsb_trending = Column(Integer, default=0)  # 0 or 1 (SQLite doesn't have boolean)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    articles = relationship("Article", back_populates="stock")
    news_items = relationship("StockNews", back_populates="stock")


class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_symbol = Column(String, ForeignKey("stocks.symbol"), index=True)
    date = Column(DateTime, index=True)
    title = Column(String)
    content = Column(Text)
    movement_type = Column(String)  # "winner", "loser", or "wsb_trending"
    slug = Column(String, unique=True, index=True)  # Unique URL: WhyDidGMEGoUp15PercentToday-Jan82026
    created_at = Column(DateTime, default=datetime.utcnow)
    
    stock = relationship("Stock", back_populates="articles")


class StockNews(Base):
    __tablename__ = "stock_news"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_symbol = Column(String, ForeignKey("stocks.symbol"), index=True)
    date = Column(DateTime, index=True)
    headline = Column(String)
    url = Column(String, nullable=True)
    source = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    stock = relationship("Stock", back_populates="news_items")

