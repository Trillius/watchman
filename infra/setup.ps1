# Discord News Bot Setup Script for Windows PowerShell
# This script automatically sets up the Discord bot environment

param(
    [switch]$SkipVenv,
    [switch]$Help
)

if ($Help) {
    Write-Host "Discord News Bot Setup Script"
    Write-Host ""
    Write-Host "Usage: .\setup.ps1 [-SkipVenv] [-Help]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -SkipVenv    Skip virtual environment creation"
    Write-Host "  -Help        Show this help message"
    Write-Host ""
    exit 0
}

Write-Host "🤖 Discord News Bot Setup" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ requirements.txt not found. Please run this script from the project root directory." -ForegroundColor Red
    exit 1
}

# Create virtual environment
if (-not $SkipVenv) {
    Write-Host ""
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    
    if (Test-Path "venv") {
        Write-Host "⚠️  Virtual environment already exists. Skipping creation." -ForegroundColor Yellow
    } else {
        python -m venv venv
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
    }
    
    # Activate virtual environment
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
}

# Install dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green

# Setup environment file
Write-Host ""
Write-Host "Setting up environment configuration..." -ForegroundColor Yellow

if (Test-Path ".env") {
    Write-Host "⚠️  .env file already exists. Skipping creation." -ForegroundColor Yellow
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file from template" -ForegroundColor Green
}

# Create logs directory
Write-Host ""
Write-Host "Creating logs directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
Write-Host "✅ Logs directory created" -ForegroundColor Green

# Generate API secret key
Write-Host ""
Write-Host "Generating API secret key..." -ForegroundColor Yellow
$apiKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# Update .env file with generated key
$envContent = Get-Content ".env" -Raw
if ($envContent -match "API_SECRET_KEY=your_api_secret_key_here") {
    $envContent = $envContent -replace "API_SECRET_KEY=your_api_secret_key_here", "API_SECRET_KEY=$apiKey"
    Set-Content ".env" $envContent
    Write-Host "✅ Generated and set API secret key" -ForegroundColor Green
} else {
    Write-Host "⚠️  API secret key already configured" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit the .env file with your Discord bot token and channel IDs" -ForegroundColor White
Write-Host "2. Create a Discord bot at https://discord.com/developers/applications" -ForegroundColor White
Write-Host "3. Invite the bot to your server with appropriate permissions" -ForegroundColor White
Write-Host "4. Run the bot with: python main.py" -ForegroundColor White
Write-Host ""
Write-Host "Configuration file: .env" -ForegroundColor Yellow
Write-Host "Required settings:" -ForegroundColor Yellow
Write-Host "  - DISCORD_TOKEN (your bot token)" -ForegroundColor White
Write-Host "  - NEWS_CHANNEL_ID (channel for news posts)" -ForegroundColor White
Write-Host "  - STATUS_CHANNEL_ID (channel for status updates)" -ForegroundColor White
Write-Host ""
Write-Host "Optional settings:" -ForegroundColor Yellow
Write-Host "  - DISCORD_GUILD_ID (for faster command sync)" -ForegroundColor White
Write-Host ""
Write-Host "To start the bot:" -ForegroundColor Green
if (-not $SkipVenv) {
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
}
Write-Host "  python main.py" -ForegroundColor White
Write-Host ""
