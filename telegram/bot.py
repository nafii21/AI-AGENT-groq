import requests
import config

def send_message(text: str):
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        raise RuntimeError("Telegram token/chat ID missing.")

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True,
    }
    r = requests.post(url, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()
