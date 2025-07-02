"""Cog for handling API events and external reports."""

from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands
from loguru import logger

from config import settings

class APIEventsCog(commands.Cog):
    """Handles events received from external API calls."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def handle_status_report(self, status_report):
        """Handle server status reports."""
        if not settings.status_channel_id:
            logger.warning("Status channel ID not configured")
            return
        
        channel = self.bot.get_channel(settings.status_channel_id)
        if not channel:
            logger.error(f"Could not find status channel with ID {settings.status_channel_id}")
            return
        
        # Choose color based on status
        color_map = {
            "online": 0x00FF00,    # Green
            "offline": 0xFF0000,   # Red
            "warning": 0xFFFF00,   # Yellow
            "error": 0xFF0000,     # Red
            "degraded": 0xFFA500   # Orange
        }
        
        color = color_map.get(status_report.status.lower(), 0x808080)  # Default gray
        
        embed = discord.Embed(
            title=f"Server Status: {status_report.server_name}",
            description=status_report.message or f"Status changed to {status_report.status}",
            color=color,
            timestamp=status_report.timestamp or datetime.now()
        )
        
        embed.add_field(name="Status", value=status_report.status.upper(), inline=True)
        embed.add_field(name="Server", value=status_report.server_name, inline=True)
        
        if status_report.metadata:
            # Add metadata fields (limit to prevent embed overflow)
            for key, value in list(status_report.metadata.items())[:5]:
                embed.add_field(name=key.title(), value=str(value), inline=True)
        
        embed.set_footer(text="Server Status Update")
        
        try:
            await channel.send(embed=embed)
            logger.info(f"Posted status update for {status_report.server_name}")
        except Exception as e:
            logger.error(f"Error posting status update: {e}")
    
    async def handle_event_report(self, event_report):
        """Handle general event reports."""
        if not settings.status_channel_id:
            logger.warning("Status channel ID not configured")
            return
        
        channel = self.bot.get_channel(settings.status_channel_id)
        if not channel:
            logger.error(f"Could not find status channel with ID {settings.status_channel_id}")
            return
        
        # Choose color based on severity
        color_map = {
            "info": 0x0099FF,      # Blue
            "warning": 0xFFFF00,   # Yellow
            "error": 0xFF6600,     # Orange
            "critical": 0xFF0000   # Red
        }
        
        color = color_map.get(event_report.severity.lower(), 0x808080)
        
        embed = discord.Embed(
            title=event_report.title,
            description=event_report.description or "No additional details provided",
            color=color,
            timestamp=event_report.timestamp or datetime.now()
        )
        
        embed.add_field(name="Event Type", value=event_report.event_type, inline=True)
        embed.add_field(name="Source", value=event_report.source, inline=True)
        embed.add_field(name="Severity", value=event_report.severity.upper(), inline=True)
        
        if event_report.metadata:
            # Add metadata fields (limit to prevent embed overflow)
            for key, value in list(event_report.metadata.items())[:3]:
                embed.add_field(name=key.title(), value=str(value), inline=True)
        
        embed.set_footer(text="Event Report")
        
        try:
            await channel.send(embed=embed)
            logger.info(f"Posted event report: {event_report.title}")
        except Exception as e:
            logger.error(f"Error posting event report: {e}")
    
    async def handle_news_update(self, news_update):
        """Handle external news updates."""
        if not settings.news_channel_id:
            logger.warning("News channel ID not configured")
            return
        
        channel = self.bot.get_channel(settings.news_channel_id)
        if not channel:
            logger.error(f"Could not find news channel with ID {settings.news_channel_id}")
            return
        
        embed = discord.Embed(
            title=news_update.title,
            description=news_update.content[:4096],  # Discord description limit
            color=0x00AAFF,  # Light blue
            timestamp=news_update.timestamp or datetime.now()
        )
        
        if news_update.url:
            embed.url = news_update.url
        
        embed.add_field(name="Source", value=news_update.source, inline=True)
        embed.set_footer(text="External News Update")
        
        try:
            await channel.send(embed=embed)
            logger.info(f"Posted external news update: {news_update.title}")
        except Exception as e:
            logger.error(f"Error posting news update: {e}")
    
    @discord.app_commands.command(name="test-api", description="Test API connectivity")
    @discord.app_commands.default_permissions(administrator=True)
    async def test_api(self, interaction: discord.Interaction):
        """Test command to verify API functionality."""
        await interaction.response.defer()
        
        # Create a test status report
        class TestStatusReport:
            def __init__(self):
                self.server_name = "Test Server"
                self.status = "online"
                self.message = "API connectivity test"
                self.timestamp = datetime.now()
                self.metadata = {"test": "true", "api_version": "1.0.0"}
        
        test_report = TestStatusReport()
        await self.handle_status_report(test_report)
        
        await interaction.followup.send("✅ API test completed! Check the status channel for the test message.")

async def setup(bot):
    await bot.add_cog(APIEventsCog(bot))
