from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from app.database import SessionLocal
from app.services.stock_service import get_daily_movers
from app.services.news_service import fetch_stock_news
from app.services.ai_service import generate_articles_for_movers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def daily_stock_analysis_job():
    """
    Main job that runs daily to:
    1. Fetch S&P 500 movers
    2. Fetch news for each stock
    3. Generate AI articles
    """
    logger.info("="*50)
    logger.info(f"Starting daily stock analysis job at {datetime.now()}")
    logger.info("="*50)
    
    db = SessionLocal()
    
    try:
        # Step 1: Get daily movers
        logger.info("Step 1: Fetching daily movers...")
        winners, losers = get_daily_movers(db, top_n=5)
        
        all_movers = winners + losers
        logger.info(f"Found {len(winners)} winners and {len(losers)} losers")
        
        # Step 2: Fetch news for each stock
        logger.info("Step 2: Fetching news for stocks...")
        for stock in all_movers:
            try:
                fetch_stock_news(db, stock.symbol, stock.name)
            except Exception as e:
                logger.error(f"Error fetching news for {stock.symbol}: {e}")
        
        # Step 3: Generate articles
        logger.info("Step 3: Generating AI articles...")
        generate_articles_for_movers(db, winners, losers)
        
        logger.info("="*50)
        logger.info("Daily stock analysis job completed successfully!")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"Error in daily stock analysis job: {e}", exc_info=True)
    finally:
        db.close()


def start_scheduler():
    """
    Start the background scheduler
    """
    logger.info("Starting scheduler...")
    
    # Schedule job to run Monday-Friday at 4:30 PM ET (after market close)
    # Note: You may need to adjust timezone based on server location
    scheduler.add_job(
        daily_stock_analysis_job,
        CronTrigger(
            day_of_week='mon-fri',
            hour=16,
            minute=30,
            timezone='America/New_York'
        ),
        id='daily_stock_analysis',
        name='Daily Stock Analysis and Article Generation',
        replace_existing=True
    )
    
    # For testing: also add a job that runs at a specific time today
    # Uncomment the lines below to test the scheduler
    # test_time = datetime.now() + timedelta(minutes=2)
    # scheduler.add_job(
    #     daily_stock_analysis_job,
    #     'date',
    #     run_date=test_time,
    #     id='test_job',
    #     name='Test Job'
    # )
    # logger.info(f"Test job scheduled for {test_time}")
    
    scheduler.start()
    logger.info("Scheduler started successfully")
    logger.info("Daily job scheduled for Mon-Fri at 4:30 PM ET")


def stop_scheduler():
    """
    Stop the background scheduler
    """
    logger.info("Stopping scheduler...")
    scheduler.shutdown()
    logger.info("Scheduler stopped")


def run_job_now():
    """
    Manually trigger the daily job (useful for testing)
    """
    logger.info("Manually triggering daily stock analysis job...")
    daily_stock_analysis_job()

