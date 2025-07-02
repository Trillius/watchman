"""Server monitoring cog for tracking bot host system status."""

import asyncio
import psutil
from datetime import datetime, timedelta
from typing import Optional

import discord
from discord.ext import commands, tasks
from loguru import logger

from config import settings

class MonitoringCog(commands.Cog):
    """Handles local server monitoring and health checks."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_alert_time = {}  # Track when alerts were last sent
        self.alert_cooldown = 300  # 5 minutes cooldown between alerts
        
    async def cog_load(self):
        """Start monitoring when cog loads."""
        if not self.system_monitor.is_running():
            self.system_monitor.start()
            logger.info("Started system monitoring task")
    
    async def cog_unload(self):
        """Stop monitoring when cog unloads."""
        if self.system_monitor.is_running():
            self.system_monitor.cancel()
            logger.info("Stopped system monitoring task")
    
    @tasks.loop(seconds=settings.monitor_interval)
    async def system_monitor(self):
        """Monitor system resources and alert on issues."""
        try:
            await self.check_system_health()
        except Exception as e:
            logger.error(f"Error in system monitor: {e}")
    
    @system_monitor.before_loop
    async def before_system_monitor(self):
        """Wait until bot is ready."""
        await self.bot.wait_until_ready()
    
    async def check_system_health(self):
        """Check system health and send alerts if necessary."""
        if not settings.status_channel_id:
            return
        
        channel = self.bot.get_channel(settings.status_channel_id)
        if not channel:
            return
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        alerts = []
        
        # CPU threshold
        if cpu_percent > 80:
            alerts.append({
                "type": "CPU",
                "message": f"High CPU usage: {cpu_percent:.1f}%",
                "severity": "warning" if cpu_percent < 90 else "critical"
            })
        
        # Memory threshold
        if memory.percent > 85:
            alerts.append({
                "type": "Memory",
                "message": f"High memory usage: {memory.percent:.1f}%",
                "severity": "warning" if memory.percent < 95 else "critical"
            })
        
        # Disk threshold
        if disk.percent > 85:
            alerts.append({
                "type": "Disk",
                "message": f"High disk usage: {disk.percent:.1f}%",
                "severity": "warning" if disk.percent < 95 else "critical"
            })
        
        # Send alerts with cooldown
        for alert in alerts:
            alert_key = f"{alert['type']}_{alert['severity']}"
            last_alert = self.last_alert_time.get(alert_key, datetime.min)
            
            if datetime.now() - last_alert > timedelta(seconds=self.alert_cooldown):
                await self.send_alert(channel, alert)
                self.last_alert_time[alert_key] = datetime.now()
    
    async def send_alert(self, channel: discord.TextChannel, alert: dict):
        """Send a system alert to Discord."""
        color_map = {
            "warning": 0xFFFF00,   # Yellow
            "critical": 0xFF0000   # Red
        }
        
        embed = discord.Embed(
            title=f"🚨 System Alert: {alert['type']}",
            description=alert['message'],
            color=color_map.get(alert['severity'], 0x808080),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Severity", value=alert['severity'].upper(), inline=True)
        embed.add_field(name="Host", value="Bot Server", inline=True)
        embed.set_footer(text="System Monitoring")
        
        try:
            await channel.send(embed=embed)
            logger.warning(f"Sent {alert['severity']} alert: {alert['message']}")
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    @discord.app_commands.command(name="status", description="Get current system status")
    async def get_system_status(self, interaction: discord.Interaction):
        """Get current system status."""
        await interaction.response.defer()
        
        try:
            # Get system information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            # Bot uptime
            bot_uptime = datetime.now() - self.bot.uptime if hasattr(self.bot, 'uptime') else None
            
            embed = discord.Embed(
                title="🖥️ System Status",
                color=0x00FF00,
                timestamp=datetime.now()
            )
            
            # System metrics
            embed.add_field(
                name="💻 CPU Usage",
                value=f"{cpu_percent:.1f}%",
                inline=True
            )
            
            embed.add_field(
                name="🧠 Memory",
                value=f"{memory.percent:.1f}% ({memory.used / 1024**3:.1f}GB / {memory.total / 1024**3:.1f}GB)",
                inline=True
            )
            
            embed.add_field(
                name="💾 Disk",
                value=f"{disk.percent:.1f}% ({disk.used / 1024**3:.1f}GB / {disk.total / 1024**3:.1f}GB)",
                inline=True
            )
            
            embed.add_field(
                name="⏰ System Uptime",
                value=f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m",
                inline=True
            )
            
            if bot_uptime:
                embed.add_field(
                    name="🤖 Bot Uptime",
                    value=f"{bot_uptime.days}d {bot_uptime.seconds//3600}h {(bot_uptime.seconds//60)%60}m",
                    inline=True
                )
            
            embed.add_field(
                name="📊 Bot Stats",
                value=f"Guilds: {len(self.bot.guilds)}\\nLatency: {self.bot.latency*1000:.0f}ms",
                inline=True
            )
            
            embed.set_footer(text="System Status Report")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            await interaction.followup.send("❌ Error retrieving system status.")
    
    @discord.app_commands.command(name="health", description="Perform system health check")
    @discord.app_commands.default_permissions(administrator=True)
    async def health_check(self, interaction: discord.Interaction):
        """Perform a comprehensive health check."""
        await interaction.response.defer()
        
        try:
            checks = []
            
            # Bot connectivity
            checks.append({
                "name": "Discord Connection",
                "status": "✅ Connected" if self.bot.is_ready() else "❌ Disconnected",
                "healthy": self.bot.is_ready()
            })
            
            # API server (if running)
            checks.append({
                "name": "API Server",
                "status": "✅ Running" if hasattr(self.bot, 'api_server') else "ℹ️ Not configured",
                "healthy": True
            })
            
            # System resources
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            checks.append({
                "name": "CPU Usage",
                "status": f"{'✅' if cpu_percent < 80 else '⚠️' if cpu_percent < 90 else '❌'} {cpu_percent:.1f}%",
                "healthy": cpu_percent < 80
            })
            
            checks.append({
                "name": "Memory Usage",
                "status": f"{'✅' if memory_percent < 85 else '⚠️' if memory_percent < 95 else '❌'} {memory_percent:.1f}%",
                "healthy": memory_percent < 85
            })
            
            checks.append({
                "name": "Disk Usage",
                "status": f"{'✅' if disk_percent < 85 else '⚠️' if disk_percent < 95 else '❌'} {disk_percent:.1f}%",
                "healthy": disk_percent < 85
            })
            
            # Overall health
            overall_healthy = all(check["healthy"] for check in checks)
            
            embed = discord.Embed(
                title="🔍 Health Check Report",
                color=0x00FF00 if overall_healthy else 0xFFFF00,
                timestamp=datetime.now()
            )
            
            for check in checks:
                embed.add_field(
                    name=check["name"],
                    value=check["status"],
                    inline=True
                )
            
            embed.add_field(
                name="Overall Status",
                value="✅ All systems healthy" if overall_healthy else "⚠️ Some issues detected",
                inline=False
            )
            
            embed.set_footer(text="Health Check Complete")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error performing health check: {e}")
            await interaction.followup.send("❌ Error performing health check.")

async def setup(bot):
    # Store bot start time
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.now()
    await bot.add_cog(MonitoringCog(bot))
