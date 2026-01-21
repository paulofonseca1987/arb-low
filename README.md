# ARB All-Time Low Tracker

Monitors the ARB (Arbitrum) token price via Binance API and sends you a Telegram notification whenever a new all-time low is reached.

Runs as a **GitHub Action** every 5 minutes, checking the price every second (~295 checks per run).

## Setup

### 1. Fork this repository

Fork this repo to your own GitHub account.

### 2. Create a Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the bot token you receive

### 3. Get your Chat ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your chat ID

### 4. Add GitHub Secrets

Go to your forked repo → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:
- `TELEGRAM_BOT_TOKEN` - Your bot token from BotFather
- `TELEGRAM_CHAT_ID` - Your chat ID

### 5. Enable GitHub Actions

Go to the Actions tab in your repo and enable workflows.

The tracker will now run every 5 minutes automatically.

## How it works

1. GitHub Actions triggers the workflow every 5 minutes
2. The script runs for ~295 seconds, checking ARB price every second via Binance API
3. ATL data is persisted using GitHub Actions cache
4. When a new ATL is detected, sends a Telegram notification

## Manual trigger

You can manually trigger the workflow from the Actions tab → "ARB Price Tracker" → "Run workflow"

## Local development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN=your_token
export TELEGRAM_CHAT_ID=your_chat_id

# Run (defaults to 295 seconds)
python arb_tracker.py

# Or run for a shorter duration for testing
RUN_DURATION=30 python arb_tracker.py
```

## Configuration

Environment variables:
- `TELEGRAM_BOT_TOKEN` - Required. Telegram bot token
- `TELEGRAM_CHAT_ID` - Required. Your Telegram chat ID
- `RUN_DURATION` - Optional. How long to run in seconds (default: 295)
- `CHECK_INTERVAL` - Optional. Seconds between price checks (default: 1)
