#!/usr/bin/env python3
"""
ARB Token All-Time Low Price Tracker

Monitors the ARB (Arbitrum) token price and sends a Telegram notification
whenever a new all-time low is reached.
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))

# CoinGecko API endpoint for ARB token
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"
ARB_TOKEN_ID = "arbitrum"

# File to persist ATL data
ATL_DATA_FILE = Path(__file__).parent / "atl_data.json"


def get_arb_price() -> float | None:
    """Fetch the current ARB token price from CoinGecko."""
    try:
        response = requests.get(
            COINGECKO_API_URL,
            params={"ids": ARB_TOKEN_ID, "vs_currencies": "usd"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data.get(ARB_TOKEN_ID, {}).get("usd")
    except requests.RequestException as e:
        print(f"Error fetching price: {e}")
        return None


def load_atl_data() -> dict:
    """Load ATL data from file."""
    if ATL_DATA_FILE.exists():
        try:
            with open(ATL_DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"atl_price": None, "atl_timestamp": None}


def save_atl_data(price: float) -> None:
    """Save ATL data to file."""
    data = {"atl_price": price, "atl_timestamp": time.time()}
    with open(ATL_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def send_telegram_message(message: str) -> bool:
    """Send a message via Telegram bot."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not configured")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(
            url,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"},
            timeout=10,
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Error sending Telegram message: {e}")
        return False


def check_and_notify() -> None:
    """Check current price and notify if new ATL."""
    current_price = get_arb_price()
    if current_price is None:
        return

    atl_data = load_atl_data()
    previous_atl = atl_data.get("atl_price")

    print(f"Current ARB price: ${current_price:.4f}")

    if previous_atl is None:
        # First run - set initial ATL
        save_atl_data(current_price)
        print(f"Initial ATL set: ${current_price:.4f}")
    elif current_price < previous_atl:
        # New ATL detected
        drop_percent = ((previous_atl - current_price) / previous_atl) * 100
        message = (
            f"<b>NEW ARB ALL-TIME LOW!</b>\n\n"
            f"Price: <b>${current_price:.4f}</b>\n"
            f"Previous ATL: ${previous_atl:.4f}\n"
            f"Drop: {drop_percent:.2f}%"
        )
        print(f"NEW ATL: ${current_price:.4f} (was ${previous_atl:.4f})")

        if send_telegram_message(message):
            print("Telegram notification sent!")
        else:
            print("Failed to send Telegram notification")

        save_atl_data(current_price)
    else:
        print(f"No new ATL (current ATL: ${previous_atl:.4f})")


def validate_config() -> bool:
    """Validate required configuration."""
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return False
    if not TELEGRAM_CHAT_ID:
        print("Error: TELEGRAM_CHAT_ID not set")
        return False
    return True


def main() -> None:
    """Main entry point."""
    print("ARB Token All-Time Low Tracker")
    print("=" * 40)

    if not validate_config():
        print("\nPlease set up your .env file with Telegram credentials.")
        print("See .env.example for reference.")
        sys.exit(1)

    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print("Starting price monitoring...\n")

    while True:
        try:
            check_and_notify()
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\nShutting down...")
            break


if __name__ == "__main__":
    main()
