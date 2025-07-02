# Discord Bot Setup Guide

## 🤖 Creating a Discord Bot

### Step 1: Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"**
3. Give it a name (e.g., "Watchman Bot")
4. Click **"Create"**

### Step 2: Create Bot User

1. In your application, go to the **"Bot"** section in the left sidebar
2. Click **"Add Bot"**
3. Click **"Yes, do it!"** to confirm

### Step 3: Get Bot Token

1. In the Bot section, under **"Token"**, click **"Reset Token"**
2. Click **"Yes, do it!"** to confirm
3. **Copy the token** (it will look like: `MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.Gxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxx`)
4. **⚠️ IMPORTANT**: Keep this token secret! Don't share it publicly.

### Step 4: Configure Bot Permissions

1. In the Bot section, enable these **Privileged Gateway Intents**:
   - ✅ Message Content Intent
   - ✅ Server Members Intent (optional)
   - ✅ Presence Intent (optional)

2. Scroll down to **Bot Permissions** and enable:
   - ✅ Send Messages
   - ✅ Use Slash Commands
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ View Channels

### Step 5: Invite Bot to Server

1. Go to **"OAuth2"** → **"URL Generator"** in the left sidebar
2. Under **"Scopes"**, select:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Under **"Bot Permissions"**, select the same permissions as Step 4
4. Copy the **Generated URL** and open it in your browser
5. Select your Discord server and click **"Authorize"**

### Step 6: Get Channel and Server IDs

1. In Discord, enable **Developer Mode**:
   - User Settings → Advanced → Developer Mode ✅

2. **Get Server ID** (Guild ID):
   - Right-click your server name → "Copy Server ID"

3. **Get Channel IDs**:
   - Right-click the channel for news → "Copy Channel ID"
   - Right-click the channel for status updates → "Copy Channel ID"

### Step 7: Update Configuration

Edit your `.env` file with the correct values:

```env
# Replace with your actual bot token (starts with MTIz... or similar)
DISCORD_TOKEN=your_actual_bot_token_here

# Replace with your server ID
DISCORD_GUILD_ID=your_server_id_here

# Replace with your channel IDs
NEWS_CHANNEL_ID=your_news_channel_id_here
STATUS_CHANNEL_ID=your_status_channel_id_here
```

### Step 8: Test the Bot

Run the bot:
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the bot
python main.py
```

## 🔍 Troubleshooting

### Common Issues:

1. **"Improper token has been passed"**
   - Token is invalid or incorrect format
   - Make sure you copied the full token from the Bot section

2. **"Missing Permissions"**
   - Bot doesn't have required permissions in the server
   - Re-invite the bot with proper permissions

3. **"Unknown Channel"**
   - Channel IDs are incorrect
   - Make sure the bot can see the channels

4. **Commands not appearing**
   - Bot needs `applications.commands` scope
   - Re-invite with proper scopes

### Valid Token Format:

Discord bot tokens typically:
- Are 70+ characters long
- Start with patterns like `MTIz...`, `NzEx...`, etc.
- Contain dots (.) separating different parts
- Look like: `MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.Gxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxx`

### Current Configuration Issues:

❌ **Token**: Current token is 64 characters (too short)  
✅ **Guild ID**: Looks correct  
✅ **Channel IDs**: Format looks correct  
✅ **API Key**: Generated correctly  

## 🎯 Next Steps

1. Get a proper Discord bot token from the Developer Portal
2. Update the `DISCORD_TOKEN` in your `.env` file
3. Run `python test_discord_config.py` to verify
4. Run `python main.py` to start the bot
5. Test slash commands in Discord (`/ping`, `/news`, `/status`)

## 🔗 Useful Links

- [Discord Developer Portal](https://discord.com/developers/applications)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord API Documentation](https://discord.com/developers/docs)
