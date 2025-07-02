"""Configuration settings for the Discord bot."""

import os
from typing import List, Optional
from pathlib import Path
from pydantic import BaseSettings, validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Bot configuration settings."""
    
    # Discord Configuration
    discord_token: str
    discord_guild_id: Optional[int] = None
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    api_secret_key: str
    
    # Database Configuration
    database_url: str = "sqlite:///./bot_data.db"
    
    # News Configuration
    news_rss_feeds: List[str] = ["https://hnrss.org/frontpage"]
    news_check_interval: int = 3600  # seconds
    news_channel_id: Optional[int] = None
    
    # Server Monitoring
    monitor_interval: int = 300  # seconds
    status_channel_id: Optional[int] = None
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/bot.log"
    
    @validator('news_rss_feeds', pre=True)
    def parse_rss_feeds(cls, v):
        """Parse comma-separated RSS feeds from environment variable."""
        if isinstance(v, str):
            return [feed.strip() for feed in v.split(',') if feed.strip()]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Create logs directory if it doesn't exist
Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)
