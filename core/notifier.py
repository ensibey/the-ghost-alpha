import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Only push signals that are truly strong alpha
TELEGRAM_MINIMUM_SCORE = 8.0

CATEGORY_EMOJI = {
    "Software": "💻",
    "Crypto": "🪙",
    "E-Commerce": "🛒",
    "B2B": "🤝",
}


def send_telegram_signal(signal_data: dict):
    """
    Send a standardized intelligence signal to Telegram.
    Only fires if signal_strength >= TELEGRAM_MINIMUM_SCORE.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram] Credentials not set. Skipping notification.")
        return

    strength = float(signal_data.get("signal_strength", 0))
    if strength < TELEGRAM_MINIMUM_SCORE:
        print(f"[Telegram] Signal score {strength} below threshold {TELEGRAM_MINIMUM_SCORE}. Suppressed.")
        return

    category = signal_data.get("category", "Unknown")
    emoji = CATEGORY_EMOJI.get(category, "🔍")
    data = signal_data.get("data", {})

    # Strength bar visualization
    filled = int(round(strength))
    bar = "█" * filled + "░" * (10 - filled)

    message = (
        f"{emoji} *GHOST ALPHA — {category.upper()} SIGNAL*\n\n"
        f"*Signal Strength:* `[{bar}] {strength}/10`\n\n"
        f"*📌 Title:* {data.get('title', 'N/A')}\n"
        f"*🔬 Insight:* {data.get('insight', 'N/A')}\n"
        f"*⚡ Action:* {signal_data.get('action_tip', 'N/A')}\n"
        f"*📡 Source:* {data.get('source', 'N/A')}\n"
    )

    # Category-specific extra fields
    if category == "Crypto" and data.get("contract_address"):
        message += f"*🔗 Contract:* `{data.get('contract_address')}`\n"
    if category == "B2B" and data.get("funding_amount"):
        message += f"*💰 Funding:* {data.get('funding_amount')}\n"
    if category == "E-Commerce" and data.get("supply_link"):
        message += f"*🏭 Supplier:* {data.get('supply_link')}\n"

    if data.get("source_url"):
        message += f"\n[🔗 View Source]({data.get('source_url')})"

    message += f"\n\n_⏱ {signal_data.get('timestamp', '')}_"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }

    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        if response.status_code == 200:
            print(f"[Telegram] ✅ Signal delivered: {data.get('title', 'N/A')} (Score: {strength})")
        else:
            print(f"[Telegram] ❌ Error {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"[Telegram] Connection error: {e}")
