#!/usr/bin/env python3
"""
ARB Token All-Time Low Price Tracker

Monitors the ARB (Arbitrum) token price via Binance API and sends a Telegram
notification whenever a new all-time low is reached.

Designed to run as a GitHub Action every 5 minutes, checking prices every second.
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

# Configuration from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RUN_DURATION = int(os.getenv("RUN_DURATION", "295"))  # seconds (slightly under 5 min)
CHECK_INTERVAL = float(os.getenv("CHECK_INTERVAL", "1"))  # seconds

# Binance API endpoint for ARB/USDT
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
SYMBOL = "ARBUSDT"

# File to persist ATL data (cached between GitHub Actions runs)
ATL_DATA_FILE = Path(__file__).parent / "atl_data.json"


def get_arb_price() -> float | None:
    """Fetch the current ARB token price from Binance."""
    try:
        response = requests.get(
            BINANCE_API_URL,
            params={"symbol": SYMBOL},
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        return float(data["price"])
    except (requests.RequestException, KeyError, ValueError) as e:
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
    data = {
        "atl_price": price,
        "atl_timestamp": datetime.utcnow().isoformat() + "Z",
    }
    with open(ATL_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"ATL data saved: ${price:.6f}")


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


def check_price(atl_price: float | None) -> tuple[float | None, bool]:
    """
    Check current price and determine if it's a new ATL.
    Returns (current_price, is_new_atl).
    """
    current_price = get_arb_price()
    if current_price is None:
        return None, False

    if atl_price is None or current_price < atl_price:
        return current_price, True

    return current_price, False


def notify_new_atl(current_price: float, previous_atl: float | None) -> None:
    """Send Telegram notification for new ATL."""
    if previous_atl is None:
        message = (
            f"<b>ARB TRACKER INITIALIZED</b>\n\n"
            f"Starting ATL: <b>${current_price:.6f}</b>"
        )
    else:
        drop_percent = ((previous_atl - current_price) / previous_atl) * 100
        message = (
            f"<b>NEW ARB ALL-TIME LOW!</b>\n\n"
            f"Price: <b>${current_price:.6f}</b>\n"
            f"Previous ATL: ${previous_atl:.6f}\n"
            f"Drop: {drop_percent:.4f}%"
        )

    if send_telegram_message(message):
        print("Telegram notification sent!")
    else:
        print("Failed to send Telegram notification")


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
    """Main entry point - runs for RUN_DURATION seconds checking every second."""
    print("ARB Token All-Time Low Tracker (Binance)")
    print("=" * 50)

    if not validate_config():
        print("\nPlease set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.")
        sys.exit(1)

    print(f"Run duration: {RUN_DURATION} seconds")
    print(f"Check interval: {CHECK_INTERVAL} second(s)")
    print("Starting price monitoring...\n")

    # Load existing ATL
    atl_data = load_atl_data()
    atl_price = atl_data.get("atl_price")

    if atl_price:
        print(f"Loaded existing ATL: ${atl_price:.6f}")
    else:
        print("No existing ATL found - will set on first price fetch")

    start_time = time.time()
    checks = 0
    errors = 0
    new_atls = 0

    while (time.time() - start_time) < RUN_DURATION:
        loop_start = time.time()
        checks += 1

        current_price, is_new_atl = check_price(atl_price)

        if current_price is None:
            errors += 1
        else:
            timestamp = datetime.utcnow().strftime("%H:%M:%S")
            status = "NEW ATL!" if is_new_atl else ""
            print(f"[{timestamp}] ARB: ${current_price:.6f} (ATL: ${atl_price or current_price:.6f}) {status}")

            if is_new_atl:
                new_atls += 1
                notify_new_atl(current_price, atl_price)
                atl_price = current_price
                save_atl_data(atl_price)

        # Sleep for remaining time in the interval
        elapsed = time.time() - loop_start
        sleep_time = max(0, CHECK_INTERVAL - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)

    # Summary
    print("\n" + "=" * 50)
    print("Run complete!")
    print(f"Total checks: {checks}")
    print(f"Errors: {errors}")
    print(f"New ATLs detected: {new_atls}")
    print(f"Final ATL: ${atl_price:.6f}" if atl_price else "No ATL recorded")


if __name__ == "__main__":
    main()
