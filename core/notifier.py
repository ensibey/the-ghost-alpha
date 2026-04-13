import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_signal(category, data_dict):
    """
    Önemli bir fırsat bulunduğunda Telegram grubuna/kanalına mesaj atar.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[!] Telegram ayarları eksik. Bildirim gönderilemedi.")
        return

    # Sinyal Seviyesine göre Emoji ata
    level = int(data_dict.get("seviye", 1))
    emoji = "🔴" if level >= 8 else ("🟡" if level >= 5 else "🟢")
    
    message = (
        f"{emoji} *GHOST ALPHA - YENİ SİNYAL*\n\n"
        f"*Kategori:* {category}\n"
        f"*Fırsat:* {data_dict.get('firsat_tipi')}\n"
        f"*Seviye:* {level}/10\n"
        f"*Neden:* {data_dict.get('neden')}\n"
        f"*Platform:* {data_dict.get('platform_ismi')}\n"
        f"*Strateji:* {data_dict.get('strateji', 'Belirtilmedi')}\n\n"
        f"[🔗 KAYNAĞA GİT]({data_dict.get('kaynak_url')})"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        if response.status_code == 200:
            print(f"[TELEGRAM] Sinyal başarıyla iletildi: {data_dict.get('firsat_tipi')}")
        else:
            print(f"[!] Telegram Hatası: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[!] Telegram Bağlantı Hatası: {e}")
