from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import stocks, articles
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="S&P 500 Stock Tracker API",
    description="Track S&P 500 winners and losers with AI-generated articles",
    version="1.0.0"
)

# CORS middleware - Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    
    # Start scheduler if enabled
    if settings.scheduler_enabled:
        from app.services.scheduler import start_scheduler
        start_scheduler()


@app.get("/")
async def root():
    return {
        "message": "S&P 500 Stock Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

