from anthropic import Anthropic
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict
import logging
import re

from app.models import Article, Stock
from app.services.news_service import get_news_summary_for_article, fetch_stock_news
from app.services.social_aggregator import get_comprehensive_social_context, format_social_context_for_ai
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


def generate_article_slug(symbol: str, price_change_pct: float, date: datetime) -> str:
    """
    Generate a unique URL slug for an article
    Example: WhyDidGMEGoUp15PercentToday-Jan82026
    """
    direction = "GoUp" if price_change_pct > 0 else "GoDown"
    abs_change = abs(int(price_change_pct))
    date_str = date.strftime("%b%d%Y")  # Jan82026
    
    slug = f"WhyDid{symbol}{direction}{abs_change}PercentToday-{date_str}"
    
    # Remove any special characters and ensure it's URL-safe
    slug = re.sub(r'[^a-zA-Z0-9-]', '', slug)
    
    return slug


def generate_article_with_claude(
    symbol: str,
    company_name: str,
    price_change_pct: float,
    price: float,
    volume: int,
    news_summary: str,
    social_context: str,
    movement_type: str
) -> Dict[str, str]:
    """
    Generate a comprehensive article by aggregating news + social media mentions
    THIS IS THE SECRET SAUCE - AI synthesizes all sources into one article
    
    Args:
        symbol: Stock ticker symbol
        company_name: Company name
        price_change_pct: Percentage change in price
        price: Current stock price
        volume: Trading volume
        news_summary: Summary of recent news articles
        social_context: Aggregated social media mentions (WSB + Twitter/X)
        movement_type: "winner" or "loser"
    
    Returns:
        Dictionary with title and content
    """
    if not settings.anthropic_api_key:
        logger.warning("ANTHROPIC_API_KEY not set, using fallback article generation")
        return generate_fallback_article(
            symbol, company_name, price_change_pct, price, volume, news_summary, movement_type
        )
    
    try:
        client = Anthropic(api_key=settings.anthropic_api_key)
        
        direction = "up" if price_change_pct > 0 else "down"
        abs_change = abs(price_change_pct)
        
        prompt = f"""You are a financial journalist. Write a comprehensive, engaging article (400-500 words) explaining why {company_name} ({symbol}) stock moved {direction} by {abs_change:.2f}% today.

📈 CURRENT STOCK DATA:
- Symbol: {symbol}
- Company: {company_name}
- Price Change: {price_change_pct:+.2f}%
- Current Price: ${price:.2f}
- Trading Volume: {volume:,}

📰 RECENT NEWS ARTICLES:
{news_summary}

{social_context}

YOUR TASK - THE SECRET SAUCE:
Synthesize ALL of the above sources (news articles, WSB comments, Twitter mentions) into ONE comprehensive, insightful article that explains:

1. WHY the stock moved today (cite specific news/events)
2. WHAT traders/investors are saying about it (reference WSB & Twitter sentiment)
3. KEY FACTORS driving the movement
4. CONTEXT that helps investors understand the bigger picture
5. Any notable technical or fundamental developments

WRITING STYLE:
- Professional yet accessible
- Reference the social sentiment naturally ("Retail traders on WallStreetBets are...")
- Cite specific tweets from trusted accounts when relevant
- Make it engaging and informative
- Write like a Bloomberg or MarketWatch article

Format your response as:
HEADLINE: [Compelling, clickable headline]

ARTICLE:
[Your comprehensive article synthesizing all sources]"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,  # Increased for longer comprehensive article
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse the response
        parts = response_text.split("ARTICLE:", 1)
        
        if len(parts) == 2:
            headline_part = parts[0].replace("HEADLINE:", "").strip()
            article_content = parts[1].strip()
        else:
            # Fallback parsing
            lines = response_text.strip().split('\n', 1)
            headline_part = lines[0].strip()
            article_content = lines[1].strip() if len(lines) > 1 else response_text
        
        logger.info(f"Generated article for {symbol} using Claude API")
        
        return {
            'title': headline_part,
            'content': article_content
        }
        
    except Exception as e:
        logger.error(f"Error generating article with Claude for {symbol}: {e}")
        return generate_fallback_article(
            symbol, company_name, price_change_pct, price, volume, news_summary, movement_type
        )


def generate_fallback_article(
    symbol: str,
    company_name: str,
    price_change_pct: float,
    price: float,
    volume: int,
    news_summary: str,
    social_context: str,
    movement_type: str
) -> Dict[str, str]:
    """
    Generate a basic article without AI when API is not available
    """
    direction = "soars" if price_change_pct > 5 else "rises" if price_change_pct > 0 else "plunges" if price_change_pct < -5 else "falls"
    abs_change = abs(price_change_pct)
    
    title = f"{company_name} ({symbol}) {direction} {abs_change:.2f}% in Today's Trading"
    
    content = f"""{company_name} ({symbol}) experienced significant movement in today's trading session, with shares {"gaining" if price_change_pct > 0 else "losing"} {abs_change:.2f}% to close at ${price:.2f}.

The stock saw notable trading volume of {volume:,} shares, indicating {"strong buying interest" if price_change_pct > 0 else "heavy selling pressure"} from investors.

Recent News Context:
{news_summary}

This price movement places {symbol} among the {"top performers" if movement_type == "winner" else "biggest decliners"} in the S&P 500 index for the day. {"Investors appear to be responding positively to recent developments" if price_change_pct > 0 else "Market concerns have weighed on the stock's performance"}.

Traders and investors should monitor upcoming earnings reports, industry trends, and broader market conditions that may continue to influence {company_name}'s stock performance in the coming sessions."""
    
    return {
        'title': title,
        'content': content
    }


def create_article_for_stock(db: Session, stock: Stock, movement_type: str) -> Article:
    """
    Create and store a COMPREHENSIVE AI-generated article for a stock
    **THE SECRET SAUCE**: Aggregates news + WSB + Twitter/X mentions into one article
    
    Args:
        db: Database session
        stock: Stock object
        movement_type: "winner" or "loser"
    
    Returns:
        Article object
    """
    logger.info(f"🔥 Generating COMPREHENSIVE article for {stock.symbol} ({movement_type})")
    
    # Step 1: Fetch news articles
    logger.info(f"  📰 Fetching news for {stock.symbol}...")
    try:
        fetch_stock_news(db, stock.symbol, stock.name)
    except Exception as e:
        logger.warning(f"  Could not fetch news: {e}")
    
    news_summary = get_news_summary_for_article(db, stock.symbol)
    
    # Step 2: Get social media context (WSB + Twitter/X)
    logger.info(f"  🔥 Aggregating social media mentions...")
    social_data = get_comprehensive_social_context(stock.symbol)
    social_context = format_social_context_for_ai(social_data)
    
    # Step 3: Generate comprehensive article using Claude (synthesizes everything)
    logger.info(f"  🤖 Generating AI article with Claude...")
    article_data = generate_article_with_claude(
        symbol=stock.symbol,
        company_name=stock.name,
        price_change_pct=stock.price_change_pct,
        price=stock.price,
        volume=stock.volume,
        news_summary=news_summary,
        social_context=social_context,
        movement_type=movement_type
    )
    
    # Generate unique slug for the article URL
    slug = generate_article_slug(stock.symbol, stock.price_change_pct, stock.date)
    
    # Create and save article
    article = Article(
        stock_symbol=stock.symbol,
        date=stock.date,
        title=article_data['title'],
        content=article_data['content'],
        movement_type=movement_type,
        slug=slug
    )
    
    db.add(article)
    db.commit()
    db.refresh(article)
    
    logger.info(f"Saved article for {stock.symbol}: {article.title} (/{slug})")
    
    return article


def generate_articles_for_movers(db: Session, winners: list, losers: list):
    """
    Generate articles for all winners and losers
    
    Args:
        db: Database session
        winners: List of Stock objects (winners)
        losers: List of Stock objects (losers)
    """
    logger.info("Generating articles for daily movers...")
    
    articles_created = 0
    
    for stock in winners:
        try:
            create_article_for_stock(db, stock, "winner")
            articles_created += 1
        except Exception as e:
            logger.error(f"Error creating article for winner {stock.symbol}: {e}")
    
    for stock in losers:
        try:
            create_article_for_stock(db, stock, "loser")
            articles_created += 1
        except Exception as e:
            logger.error(f"Error creating article for loser {stock.symbol}: {e}")
    
    logger.info(f"Successfully created {articles_created} articles")

