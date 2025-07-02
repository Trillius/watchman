from dotenv import load_dotenv
import os
load_dotenv()

"""Main Discord bot application."""

import asyncio
import sys
from pathlib import Path

import discord
from discord.ext import commands
from loguru import logger

from config import settings
from api.server import start_api_server

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    settings.log_file,
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="10 MB",
    retention="30 days"
)

class NewsBot(commands.Bot):
    """Discord bot for news reporting and server monitoring."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description="News reporting and server monitoring bot"
        )
        
    async def setup_hook(self):
        """Called when the bot is starting up."""
        logger.info("Setting up bot...")
        
        # Load cogs
        cogs_to_load = [
            "cogs.news",
            "cogs.monitoring", 
            "cogs.general",
            "cogs.api_events"
        ]
        
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")
        
        # Start API server
        asyncio.create_task(start_api_server(self))
        
        # Sync slash commands
        if settings.discord_guild_id:
            guild = discord.Object(id=settings.discord_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f"Synced commands to guild {settings.discord_guild_id}")
        else:
            await self.tree.sync()
            logger.info("Synced commands globally")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"{self.user} has connected to Discord!")
        logger.info(f"Bot is in {len(self.guilds)} guilds")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for news and server status"
            )
        )

async def main():
    """Main entry point."""
    bot = NewsBot()
    
    try:
        await bot.start(settings.discord_token)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
