# Setup Guide

## Prerequisites
- Python 3.9+
- Discord bot token
- Docker (optional)
- `.env` file with required environment variables

## Installation (Dev)
```bash
git clone https://github.com/yourname/watchman.git
cd watchman
pip install -r requirements.txt
python bot/main.py
```

## Run with Docker
```bash
cd infra
docker-compose up --build
```
