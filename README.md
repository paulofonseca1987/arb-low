# ARB All-Time Low Tracker

Monitors the ARB (Arbitrum) token price and sends you a Telegram notification whenever a new all-time low is reached.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the bot token you receive

### 3. Get your Chat ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your chat ID

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
CHECK_INTERVAL=60
```

### 5. Run the tracker

```bash
python arb_tracker.py
```

## How it works

- Fetches ARB price from CoinGecko API every 60 seconds (configurable)
- Stores the all-time low price in `atl_data.json`
- Sends a Telegram message when a new all-time low is detected

## Running as a service

To run continuously in the background, you can use `screen`, `tmux`, or create a systemd service.

Example with screen:
```bash
screen -S arb-tracker
python arb_tracker.py
# Press Ctrl+A, then D to detach
```
