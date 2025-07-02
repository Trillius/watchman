# Discord News & Monitoring Bot

A comprehensive Discord bot that provides news reporting from Hacker News, server monitoring capabilities, and accepts external API calls for event reporting. Built with modern Python techniques using discord.py 2.x, FastAPI, and a modular cog-based architecture.

## Features

- 📰 **Hacker News Integration**: Automatically fetches and posts the latest stories from Hacker News frontpage
- 🖥️ **System Monitoring**: Real-time monitoring of CPU, memory, and disk usage with configurable alerts
- 🔗 **External API**: RESTful API endpoints to receive status reports and events from other systems
- ⚡ **Slash Commands**: Modern Discord slash commands for interactive functionality
- 📊 **Health Checks**: Comprehensive system health monitoring and reporting
- 🔧 **Modular Design**: Cog-based architecture for easy maintenance and feature additions

## Project Structure

```
discord-news-bot/
├── main.py                 # Bot entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
├── .gitignore             # Git ignore rules
├── setup.sh               # Automated setup script (Unix/Linux)
├── setup.ps1              # Automated setup script (Windows PowerShell)
├── config/
│   ├── __init__.py
│   └── settings.py        # Configuration management
├── cogs/
│   ├── __init__.py
│   ├── news.py           # Hacker News integration
│   ├── monitoring.py     # System monitoring
│   ├── general.py        # General bot commands
│   └── api_events.py     # External API event handling
├── api/
│   ├── __init__.py
│   └── server.py         # FastAPI server
└── logs/                 # Log files (created automatically)
```

## Prerequisites

- Python 3.8 or higher
- Discord Bot Token ([Create one here](https://discord.com/developers/applications))
- Discord Server with appropriate permissions

## Quick Setup

### Windows (PowerShell)

1. **Clone the repository**:
   ```powershell
   git clone <your-repo-url>
   cd discord-news-bot
   ```

2. **Run the automated setup script**:
   ```powershell
   .\setup.ps1
   ```

### Linux/macOS (Bash)

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd discord-news-bot
   ```

2. **Run the automated setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

### Manual Setup

1. **Create a virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the bot**:
   ```bash
   python main.py
   ```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

#### Required Settings

- `DISCORD_TOKEN`: Your Discord bot token
- `API_SECRET_KEY`: Secret key for API authentication (generate a strong random string)

#### Optional Settings

- `DISCORD_GUILD_ID`: Guild ID for faster command syncing (recommended for development)
- `NEWS_CHANNEL_ID`: Channel ID where news will be posted
- `STATUS_CHANNEL_ID`: Channel ID where status updates and alerts will be posted
- `API_HOST`: API server host (default: 0.0.0.0)
- `API_PORT`: API server port (default: 8080)
- `NEWS_CHECK_INTERVAL`: How often to check for news in seconds (default: 3600)
- `MONITOR_INTERVAL`: How often to check system status in seconds (default: 300)

### Discord Bot Setup

1. **Create a Discord Application**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name
   - Go to the "Bot" section and click "Add Bot"
   - Copy the bot token and add it to your `.env` file

2. **Bot Permissions**:
   The bot needs the following permissions:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Read Message History

3. **Invite the Bot**:
   - Go to the "OAuth2" > "URL Generator" section
   - Select "bot" and "applications.commands" scopes
   - Select the required permissions
   - Use the generated URL to invite the bot to your server

### Channel Setup

1. **Create dedicated channels** (recommended):
   - `#news` - For Hacker News posts
   - `#status` - For system status and alerts

2. **Get Channel IDs**:
   - Enable Developer Mode in Discord settings
   - Right-click on channels and select "Copy ID"
   - Add the IDs to your `.env` file

## API Endpoints

The bot includes a FastAPI server that accepts external reports:

### Authentication

All API endpoints require Bearer token authentication using the `API_SECRET_KEY`.

```bash
curl -H "Authorization: Bearer YOUR_API_SECRET_KEY" \
     -H "Content-Type: application/json" \
     http://localhost:8080/health
```

### Available Endpoints

#### Health Check
```http
GET /health
```
Returns bot and API server status.

#### Status Reports
```http
POST /status
Content-Type: application/json
Authorization: Bearer YOUR_API_SECRET_KEY

{
    "server_name": "Web Server 01",
    "status": "online",
    "message": "All services running normally",
    "metadata": {
        "version": "1.2.3",
        "uptime": "5d 12h 30m"
    }
}
```

#### Event Reports
```http
POST /event
Content-Type: application/json
Authorization: Bearer YOUR_API_SECRET_KEY

{
    "event_type": "deployment",
    "source": "CI/CD Pipeline",
    "title": "Application Deployed",
    "description": "Version 2.1.0 deployed successfully",
    "severity": "info",
    "metadata": {
        "version": "2.1.0",
        "environment": "production"
    }
}
```

#### News Updates
```http
POST /news
Content-Type: application/json
Authorization: Bearer YOUR_API_SECRET_KEY

{
    "title": "Important System Update",
    "content": "System maintenance scheduled for tonight",
    "source": "System Admin",
    "url": "https://example.com/maintenance"
}
```

## Slash Commands

The bot provides several slash commands:

- `/news [count]` - Get latest Hacker News stories (1-10)
- `/status` - Get current system status
- `/health` - Perform comprehensive health check (admin only)
- `/test-api` - Test API connectivity (admin only)

## Development

### Adding New Features

1. **Create a new cog**:
   ```python
   # cogs/your_feature.py
   from discord.ext import commands

   class YourFeatureCog(commands.Cog):
       def __init__(self, bot):
           self.bot = bot

   async def setup(bot):
       await bot.add_cog(YourFeatureCog(bot))
   ```

2. **Load the cog in main.py**:
   ```python
   cogs_to_load = [
       "cogs.news",
       "cogs.monitoring",
       "cogs.general",
       "cogs.api_events",
       "cogs.your_feature"  # Add your new cog
   ]
   ```

### Running in Development

1. **Set development environment**:
   ```bash
   # Add to .env
   LOG_LEVEL=DEBUG
   DISCORD_GUILD_ID=your_test_server_id
   ```

2. **Run with auto-reload** (requires `watchdog`):
   ```bash
   pip install watchdog
   python -m main
   ```

## Deployment

### Kubernetes Deployment

#### Prerequisites

- [Kubernetes](https://kubernetes.io) cluster (v1.19+ recommended)
- [Helm](https://helm.sh) v3

#### Setup Helm

1. **Add Repo** (if not added already)
   ```sh
   helm repo add stable https://charts.helm.sh/stable
   helm repo update
   ```

2. **Navigate to Helm Directory**
   ```sh
   cd helm/watchman
   ```

3. **Install Chart**
   ```sh
   helm install watchman .
   ```

4. **Upgrade Chart**
   ```sh
   helm upgrade watchman .
   ```

5. **Uninstall Chart**
   ```sh
   helm uninstall watchman
   ```

#### Secrets Configuration

- **Discord Token**: Stored as Kubernetes Secret via Helm (`values.yaml` or directly via `Secret`)
- **API Secret Key**: Custom-generated or predefined by user

Example:
```sh
kubectl create secret generic watchman-secrets --from-literal=discord-token="YOUR_DISCORD_TOKEN" --from-literal=api-secret-key="YOUR_API_SECRET"
```

#### Monitoring and Access

- **Service**: Exposes bot with type `ClusterIP` on port `8080`
- **Ingress**: Optional ingress setup for external access
- **Monitoring**: Configurable via Prometheus (use `serviceMonitor` if enabled)

### Docker Deployment

1. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .
   CMD ["python", "main.py"]
   ```

2. **Build and run**:
   ```bash
   docker build -t discord-news-bot .
   docker run -d --name news-bot --env-file .env discord-news-bot
   ```

### Systemd Service (Linux)

1. **Create service file** (`/etc/systemd/system/discord-bot.service`):
   ```ini
   [Unit]
   Description=Discord News Bot
   After=network.target

   [Service]
   Type=simple
   User=your-user
   WorkingDirectory=/path/to/discord-news-bot
   Environment=PATH=/path/to/discord-news-bot/venv/bin
   ExecStart=/path/to/discord-news-bot/venv/bin/python main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable discord-bot
   sudo systemctl start discord-bot
   ```

## Monitoring & Logs

### Log Files

Logs are automatically rotated and stored in the `logs/` directory:
- **File**: `logs/bot.log`
- **Rotation**: 10 MB per file
- **Retention**: 30 days

### Log Levels

Configure logging level in `.env`:
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about bot operations
- `WARNING`: Warning messages and non-critical issues
- `ERROR`: Error messages and exceptions

### Health Monitoring

The bot includes built-in health monitoring:
- **System Resources**: CPU, memory, disk usage alerts
- **Discord Connectivity**: Connection status monitoring
- **API Server**: FastAPI server health checks

## Troubleshooting

### Common Issues

1. **Bot not responding to commands**:
   - Check if bot has proper permissions
   - Verify `DISCORD_TOKEN` is correct
   - Ensure bot is invited with `applications.commands` scope

2. **News not posting**:
   - Verify `NEWS_CHANNEL_ID` is set and correct
   - Check bot has permission to send messages in the channel
   - Check logs for RSS feed errors

3. **API endpoints not working**:
   - Verify `API_SECRET_KEY` is set
   - Check if port is available and not blocked by firewall
   - Test with `/health` endpoint first

4. **High resource usage alerts**:
   - Check system resources with `/status` command
   - Review running processes
   - Consider adjusting monitoring thresholds in code

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

Check logs for detailed information:
```bash
tail -f logs/bot.log
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit with descriptive messages
5. Push to your fork and create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check this README and troubleshooting section
2. Review logs for error messages
3. Create an issue on GitHub with detailed information

## Changelog

### v1.0.0
- Initial release
- Hacker News integration
- System monitoring
- FastAPI external events
- Slash commands support
- Comprehensive logging and health checks
