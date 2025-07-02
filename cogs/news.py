"""News cog for fetching and posting Hacker News stories."""

import asyncio
import aiohttp
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Any

import discord
from discord.ext import commands, tasks
from loguru import logger

from config import settings

class NewsCog(commands.Cog):
    """Handles news fetching and posting."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_check = datetime.now() - timedelta(hours=1)
        self.posted_stories = set()  # Track posted story IDs to avoid duplicates
        
    async def cog_load(self):
        """Start the news checking task when cog loads."""
        if not self.news_checker.is_running():
            self.news_checker.start()
            logger.info("Started news checker task")
    
    async def cog_unload(self):
        """Stop the news checking task when cog unloads."""
        if self.news_checker.is_running():
            self.news_checker.cancel()
            logger.info("Stopped news checker task")
    
    @tasks.loop(seconds=settings.news_check_interval)
    async def news_checker(self):
        """Periodically check for new stories."""
        try:
            await self.fetch_and_post_news()
        except Exception as e:
            logger.error(f"Error in news checker: {e}")
    
    @news_checker.before_loop
    async def before_news_checker(self):
        """Wait until the bot is ready before starting the task."""
        await self.bot.wait_until_ready()
    
    async def fetch_and_post_news(self):
        """Fetch news from RSS feeds and post new stories."""
        if not settings.news_channel_id:
            logger.warning("News channel ID not configured")
            return
        
        channel = self.bot.get_channel(settings.news_channel_id)
        if not channel:
            logger.error(f"Could not find news channel with ID {settings.news_channel_id}")
            return
        
        new_stories = []
        
        for feed_url in settings.news_rss_feeds:
            try:
                stories = await self.fetch_rss_feed(feed_url)
                new_stories.extend(stories)
            except Exception as e:
                logger.error(f"Error fetching feed {feed_url}: {e}")
        
        # Sort stories by publication date (newest first)
        new_stories.sort(key=lambda x: x.get('published_parsed', (0,)), reverse=True)
        
        # Post new stories (limit to avoid spam)
        posted_count = 0
        max_posts_per_check = 5
        
        for story in new_stories:
            if posted_count >= max_posts_per_check:
                break
                
            story_id = story.get('id', story.get('link', ''))
            if story_id in self.posted_stories:
                continue
            
            # Check if story is newer than last check
            story_date = datetime(*story.get('published_parsed', (0,0,0,0,0,0))[:6])
            if story_date <= self.last_check:
                continue
            
            await self.post_story(channel, story)
            self.posted_stories.add(story_id)
            posted_count += 1
            
            # Add small delay between posts
            await asyncio.sleep(1)
        
        if posted_count > 0:
            logger.info(f"Posted {posted_count} new stories")
        
        self.last_check = datetime.now()
        
        # Clean up old posted story IDs (keep last 1000)
        if len(self.posted_stories) > 1000:
            self.posted_stories = set(list(self.posted_stories)[-500:])
    
    async def fetch_rss_feed(self, feed_url: str) -> List[Dict[str, Any]]:
        """Fetch and parse RSS feed."""
        async with aiohttp.ClientSession() as session:
            async with session.get(feed_url) as response:
                content = await response.text()
                
        feed = feedparser.parse(content)
        return feed.entries
    
    async def post_story(self, channel: discord.TextChannel, story: Dict[str, Any]):
        """Post a single story to Discord."""
        title = story.get('title', 'No title')
        link = story.get('link', '')
        summary = story.get('summary', '')
        author = story.get('author', 'Unknown')
        
        # Create embed
        embed = discord.Embed(
            title=title[:256],  # Discord title limit
            url=link,
            description=summary[:4096] if summary else "No summary available",
            color=0xFF6600,  # Hacker News orange
            timestamp=datetime.now()
        )
        
        embed.set_author(name="Hacker News", icon_url="https://news.ycombinator.com/favicon.ico")
        embed.add_field(name="Author", value=author, inline=True)
        
        # Add comments link if available
        comments_link = story.get('comments', '')
        if comments_link:
            embed.add_field(name="Comments", value=f"[View Comments]({comments_link})", inline=True)
        
        embed.set_footer(text="Hacker News • Frontpage")
        
        try:
            await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error posting story: {e}")
    
    @discord.app_commands.command(name="news", description="Get latest Hacker News stories")
    async def get_latest_news(self, interaction: discord.Interaction, count: int = 5):
        """Slash command to get latest news stories."""
        await interaction.response.defer()
        
        if count > 10:
            count = 10
        elif count < 1:
            count = 1
        
        try:
            stories = []
            for feed_url in settings.news_rss_feeds:
                feed_stories = await self.fetch_rss_feed(feed_url)
                stories.extend(feed_stories[:count])
            
            # Sort and limit
            stories.sort(key=lambda x: x.get('published_parsed', (0,)), reverse=True)
            stories = stories[:count]
            
            if not stories:
                await interaction.followup.send("No stories found.")
                return
            
            embeds = []
            for story in stories:
                title = story.get('title', 'No title')
                link = story.get('link', '')
                summary = story.get('summary', '')
                
                embed = discord.Embed(
                    title=title[:256],
                    url=link,
                    description=summary[:200] + "..." if len(summary) > 200 else summary,
                    color=0xFF6600
                )
                embeds.append(embed)
            
            # Send embeds (Discord limit is 10 per message)
            for embed in embeds:
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in news command: {e}")
            await interaction.followup.send("Error fetching news stories.")
    
    @commands.command(name="testnews")
    @commands.has_permissions(administrator=True)
    async def test_news_fetch(self, ctx):
        """Test command to manually trigger news fetch."""
        await ctx.send("Fetching latest news...")
        await self.fetch_and_post_news()
        await ctx.send("News fetch completed.")

async def setup(bot):
    await bot.add_cog(NewsCog(bot))
