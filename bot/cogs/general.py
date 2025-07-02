"""General bot commands and utilities."""

from datetime import datetime
import discord
from discord.ext import commands
from loguru import logger

from config import settings

class GeneralCog(commands.Cog):
    """General bot commands and utilities."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @discord.app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Check bot latency."""
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: **{latency}ms**",
            color=0x00FF00 if latency < 100 else 0xFFFF00 if latency < 200 else 0xFF0000,
            timestamp=datetime.now()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @discord.app_commands.command(name="info", description="Get bot information")
    async def bot_info(self, interaction: discord.Interaction):
        """Get bot information."""
        bot_user = self.bot.user
        
        embed = discord.Embed(
            title="🤖 Bot Information",
            color=0x7289DA,
            timestamp=datetime.now()
        )
        
        embed.set_thumbnail(url=bot_user.avatar.url if bot_user.avatar else bot_user.default_avatar.url)
        
        embed.add_field(
            name="Bot Name",
            value=bot_user.display_name,
            inline=True
        )
        
        embed.add_field(
            name="Bot ID",
            value=bot_user.id,
            inline=True
        )
        
        embed.add_field(
            name="Servers",
            value=len(self.bot.guilds),
            inline=True
        )
        
        embed.add_field(
            name="Latency",
            value=f"{round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        embed.add_field(
            name="API Port",
            value=settings.api_port,
            inline=True
        )
        
        embed.add_field(
            name="News Source",
            value="Hacker News",
            inline=True
        )
        
        embed.add_field(
            name="Features",
            value="• 📰 News Reporting\n• 🖥️ System Monitoring\n• 🔗 External API\n• ⚡ Slash Commands",
            inline=False
        )
        
        embed.set_footer(text="Discord News & Monitoring Bot")
        
        await interaction.response.send_message(embed=embed)
    
    @discord.app_commands.command(name="help", description="Get help information")
    async def help_command(self, interaction: discord.Interaction):
        """Get help information."""
        embed = discord.Embed(
            title="📚 Help - Available Commands",
            description="Here are all the available slash commands:",
            color=0x7289DA,
            timestamp=datetime.now()
        )
        
        # General commands
        embed.add_field(
            name="🔧 General Commands",
            value="`/ping` - Check bot latency\n"
                  "`/info` - Get bot information\n"
                  "`/help` - Show this help message",
            inline=False
        )
        
        # News commands
        embed.add_field(
            name="📰 News Commands",
            value="`/news [count]` - Get latest Hacker News stories (1-10)",
            inline=False
        )
        
        # Monitoring commands
        embed.add_field(
            name="🖥️ Monitoring Commands",
            value="`/status` - Get current system status\n"
                  "`/health` - Perform health check (admin only)",
            inline=False
        )
        
        # API commands
        embed.add_field(
            name="🔗 API Commands",
            value="`/test-api` - Test API connectivity (admin only)",
            inline=False
        )
        
        # API endpoints
        embed.add_field(
            name="🌐 API Endpoints",
            value=f"The bot exposes an API on port {settings.api_port}:\n"
                  f"• `GET /health` - Health check\n"
                  f"• `POST /status` - Submit status reports\n"
                  f"• `POST /event` - Submit event reports\n"
                  f"• `POST /news` - Submit news updates\n\n"
                  f"All POST endpoints require API key authentication.",
            inline=False
        )
        
        embed.set_footer(text="For detailed setup instructions, check the README.md file")
        
        await interaction.response.send_message(embed=embed)
    
    @commands.command(name="reload")
    @commands.has_permissions(administrator=True)
    async def reload_cog(self, ctx, *, cog_name: str = None):
        """Reload a specific cog or all cogs."""
        if cog_name is None:
            await ctx.send("Please specify a cog name to reload.")
            return
        
        try:
            await self.bot.reload_extension(f"cogs.{cog_name}")
            await ctx.send(f"✅ Reloaded cog: {cog_name}")
            logger.info(f"Reloaded cog: {cog_name}")
        except commands.ExtensionNotLoaded:
            await ctx.send(f"❌ Cog '{cog_name}' is not loaded.")
        except commands.ExtensionNotFound:
            await ctx.send(f"❌ Cog '{cog_name}' not found.")
        except Exception as e:
            await ctx.send(f"❌ Error reloading cog '{cog_name}': {e}")
            logger.error(f"Error reloading cog {cog_name}: {e}")
    
    @commands.command(name="listcogs")
    @commands.has_permissions(administrator=True)
    async def list_cogs(self, ctx):
        """List all loaded cogs."""
        cogs = list(self.bot.cogs.keys())
        if cogs:
            cog_list = "\n".join([f"• {cog}" for cog in cogs])
            embed = discord.Embed(
                title="📦 Loaded Cogs",
                description=cog_list,
                color=0x00FF00,
                timestamp=datetime.now()
            )
        else:
            embed = discord.Embed(
                title="📦 Loaded Cogs",
                description="No cogs are currently loaded.",
                color=0xFF0000,
                timestamp=datetime.now()
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="sync")
    @commands.has_permissions(administrator=True)
    async def sync_commands(self, ctx):
        """Sync slash commands."""
        try:
            if settings.discord_guild_id:
                guild = discord.Object(id=settings.discord_guild_id)
                self.bot.tree.copy_global_to(guild=guild)
                synced = await self.bot.tree.sync(guild=guild)
                await ctx.send(f"✅ Synced {len(synced)} commands to guild {settings.discord_guild_id}")
            else:
                synced = await self.bot.tree.sync()
                await ctx.send(f"✅ Synced {len(synced)} commands globally")
            
            logger.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            await ctx.send(f"❌ Error syncing commands: {e}")
            logger.error(f"Error syncing commands: {e}")

async def setup(bot):
    await bot.add_cog(GeneralCog(bot))
