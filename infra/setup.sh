#!/bin/bash

# Discord News Bot Setup Script for Unix/Linux/macOS
# This script automatically sets up the Discord bot environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Help function
show_help() {
    echo "Discord News Bot Setup Script"
    echo ""
    echo "Usage: ./setup.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --skip-venv    Skip virtual environment creation"
    echo "  --help         Show this help message"
    echo ""
}

# Parse command line arguments
SKIP_VENV=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-venv)
            SKIP_VENV=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

echo -e "${CYAN}🤖 Discord News Bot Setup${NC}"
echo -e "${CYAN}=========================${NC}"
echo ""

# Check Python installation
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✅ Found: $PYTHON_VERSION${NC}"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version 2>&1)
    # Check if it's Python 3
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        echo -e "${GREEN}✅ Found: $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}❌ Python 3 required, but found: $PYTHON_VERSION${NC}"
        echo -e "${RED}Please install Python 3.8+ from https://python.org${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Python not found. Please install Python 3.8+ from https://python.org${NC}"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt not found. Please run this script from the project root directory.${NC}"
    exit 1
fi

# Create virtual environment
if [ "$SKIP_VENV" = false ]; then
    echo ""
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    
    if [ -d "venv" ]; then
        echo -e "${YELLOW}⚠️  Virtual environment already exists. Skipping creation.${NC}"
    else
        $PYTHON_CMD -m venv venv
        echo -e "${GREEN}✅ Virtual environment created${NC}"
    fi
    
    # Activate virtual environment
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
fi

# Install dependencies
echo ""
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✅ Dependencies installed successfully${NC}"

# Setup environment file
echo ""
echo -e "${YELLOW}Setting up environment configuration...${NC}"

if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists. Skipping creation.${NC}"
else
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file from template${NC}"
fi

# Create logs directory
echo ""
echo -e "${YELLOW}Creating logs directory...${NC}"
mkdir -p logs
echo -e "${GREEN}✅ Logs directory created${NC}"

# Generate API secret key
echo ""
echo -e "${YELLOW}Generating API secret key...${NC}"
API_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)

# Update .env file with generated key
if grep -q "API_SECRET_KEY=your_api_secret_key_here" .env; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/API_SECRET_KEY=your_api_secret_key_here/API_SECRET_KEY=$API_KEY/" .env
    else
        # Linux
        sed -i "s/API_SECRET_KEY=your_api_secret_key_here/API_SECRET_KEY=$API_KEY/" .env
    fi
    echo -e "${GREEN}✅ Generated and set API secret key${NC}"
else
    echo -e "${YELLOW}⚠️  API secret key already configured${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo -e "${NC}1. Edit the .env file with your Discord bot token and channel IDs${NC}"
echo -e "${NC}2. Create a Discord bot at https://discord.com/developers/applications${NC}"
echo -e "${NC}3. Invite the bot to your server with appropriate permissions${NC}"
echo -e "${NC}4. Run the bot with: python main.py${NC}"
echo ""
echo -e "${YELLOW}Configuration file: .env${NC}"
echo -e "${YELLOW}Required settings:${NC}"
echo -e "${NC}  - DISCORD_TOKEN (your bot token)${NC}"
echo -e "${NC}  - NEWS_CHANNEL_ID (channel for news posts)${NC}"
echo -e "${NC}  - STATUS_CHANNEL_ID (channel for status updates)${NC}"
echo ""
echo -e "${YELLOW}Optional settings:${NC}"
echo -e "${NC}  - DISCORD_GUILD_ID (for faster command sync)${NC}"
echo ""
echo -e "${GREEN}To start the bot:${NC}"
if [ "$SKIP_VENV" = false ]; then
    echo -e "${NC}  source venv/bin/activate${NC}"
fi
echo -e "${NC}  python main.py${NC}"
echo ""
