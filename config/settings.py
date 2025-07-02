"""Configuration settings for the Discord bot."""

import os
from typing import List, Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Bot configuration settings."""
    
    # Discord Configuration
    discord_token: str = "your_discord_bot_token_here"
    discord_guild_id: Optional[int] = None
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    api_secret_key: str = "change_me"
    
    # Database Configuration
    database_url: str = "sqlite:///./bot_data.db"
    
    # News Configuration
    news_rss_feeds: str = "https://hnrss.org/frontpage"
    news_check_interval: int = 3600  # seconds
    news_channel_id: Optional[int] = None
    
    # Server Monitoring
    monitor_interval: int = 300  # seconds
    status_channel_id: Optional[int] = None
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/bot.log"
    
    def get_news_feeds_list(self) -> List[str]:
        """Parse comma-separated RSS feeds from string."""
        if isinstance(self.news_rss_feeds, str):
            return [feed.strip() for feed in self.news_rss_feeds.split(',') if feed.strip()]
        return [self.news_rss_feeds]
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }

# Global settings instance
settings = Settings()

# Create logs directory if it doesn't exist
Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)
