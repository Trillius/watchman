"""FastAPI server for receiving external events and status updates."""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
from loguru import logger

from config import settings

# Security
security = HTTPBearer()

# API Models
class StatusReport(BaseModel):
    """Model for server status reports."""
    server_name: str
    status: str  # "online", "offline", "warning", "error"
    message: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class EventReport(BaseModel):
    """Model for general event reports."""
    event_type: str
    source: str
    title: str
    description: Optional[str] = None
    severity: str = "info"  # "info", "warning", "error", "critical"
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class NewsUpdate(BaseModel):
    """Model for external news updates."""
    title: str
    content: str
    source: str
    url: Optional[str] = None
    timestamp: Optional[datetime] = None

# Global reference to Discord bot
discord_bot = None

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key authentication."""
    if credentials.credentials != settings.api_secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return credentials.credentials

# Create FastAPI app
app = FastAPI(
    title="Discord Bot API",
    description="API for receiving external events and status updates",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "bot_connected": discord_bot.is_ready() if discord_bot else False
    }

@app.post("/status")
async def report_status(
    status_report: StatusReport,
    api_key: str = Depends(verify_api_key)
):
    """Receive server status reports."""
    try:
        if not discord_bot or not discord_bot.is_ready():
            raise HTTPException(status_code=503, detail="Discord bot not ready")
        
        # Get the API events cog to handle the status report
        api_cog = discord_bot.get_cog("APIEventsCog")
        if not api_cog:
            raise HTTPException(status_code=503, detail="API events cog not loaded")
        
        await api_cog.handle_status_report(status_report)
        
        logger.info(f"Received status report from {status_report.server_name}: {status_report.status}")
        return {"message": "Status report received", "timestamp": datetime.now()}
        
    except Exception as e:
        logger.error(f"Error processing status report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/event")
async def report_event(
    event_report: EventReport,
    api_key: str = Depends(verify_api_key)
):
    """Receive general event reports."""
    try:
        if not discord_bot or not discord_bot.is_ready():
            raise HTTPException(status_code=503, detail="Discord bot not ready")
        
        api_cog = discord_bot.get_cog("APIEventsCog")
        if not api_cog:
            raise HTTPException(status_code=503, detail="API events cog not loaded")
        
        await api_cog.handle_event_report(event_report)
        
        logger.info(f"Received event report: {event_report.event_type} from {event_report.source}")
        return {"message": "Event report received", "timestamp": datetime.now()}
        
    except Exception as e:
        logger.error(f"Error processing event report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/news")
async def submit_news(
    news_update: NewsUpdate,
    api_key: str = Depends(verify_api_key)
):
    """Receive external news submissions."""
    try:
        if not discord_bot or not discord_bot.is_ready():
            raise HTTPException(status_code=503, detail="Discord bot not ready")
        
        api_cog = discord_bot.get_cog("APIEventsCog")
        if not api_cog:
            raise HTTPException(status_code=503, detail="API events cog not loaded")
        
        await api_cog.handle_news_update(news_update)
        
        logger.info(f"Received news update: {news_update.title} from {news_update.source}")
        return {"message": "News update received", "timestamp": datetime.now()}
        
    except Exception as e:
        logger.error(f"Error processing news update: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def start_api_server(bot):
    """Start the API server."""
    global discord_bot
    discord_bot = bot
    
    config = uvicorn.Config(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    logger.info(f"Starting API server on {settings.api_host}:{settings.api_port}")
    await server.serve()
