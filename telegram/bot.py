import requests
import config

class TelegramError(RuntimeError):
    pass

def send_message(text: str, parse_mode: str = None) -> dict:
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        raise RuntimeError("Telegram token or chat ID is missing in config.")

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True,
    }

    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        r = requests.post(url, json=payload, timeout=20)
        res_data = r.json()

        if not res_data.get("ok"):
            error_desc = res_data.get("description", "Unknown Telegram API error")
            print(f"[TELEGRAM ERROR] Failed to send message: {error_desc}")
            raise TelegramError(f"Telegram API Error: {error_desc}")

        return res_data
    except requests.exceptions.RequestException as exc:
        print(f"[TELEGRAM ERROR] Network issue: {exc}")
        raise TelegramError(f"Network error while sending Telegram message: {exc}") from exc

def process_incoming_updates(state: dict) -> dict:
    """
    Cek pesan masuk (/start, /status) dari Telegram
    dan merespons sesuai workflow & state bot saat ini.
    """
    if not config.TELEGRAM_BOT_TOKEN:
        return state

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/getUpdates"
    
    offset = state.get("telegram_offset", 0)
    params = {
        "offset": offset,
        "timeout": 1,
        "allowed_updates": ["message"]
    }

    try:
        r = requests.get(url, params=params, timeout=5)
        res = r.json()
        if not res.get("ok"):
            return state

        updates = res.get("result", [])
        for update in updates:
            update_id = update["update_id"]
            state["telegram_offset"] = update_id + 1

            message = update.get("message", {})
            text = message.get("text", "").strip()
            chat_id = str(message.get("chat", {}).get("id", ""))

            # Hanya merespons jika pesan berasal dari TELEGRAM_CHAT_ID milikmu
            if chat_id != str(config.TELEGRAM_CHAT_ID):
                continue

            if text == "/start":
                reply = (
                    "🤖 *AI TRADING AGENT V1 IS ACTIVE*\n\n"
                    f"📌 *Symbol:* {config.SYMBOL}\n"
                    f"📐 *Strategy:* Daily POI + M15 Engulfing\n"
                    f"🧠 *AI Filter:* Groq ({config.GROQ_MODEL})\n"
                    f"⚙️ *Min Confidence:* {config.MIN_AI_CONFIDENCE}%\n"
                    f"🎯 *Max Signals/Day:* {config.MAX_TRADES_PER_DAY}\n\n"
                    "Status: *Monitoring market 24/7...*"
                )
                send_message(reply, parse_mode="Markdown")

            elif text == "/status":
                reply = (
                    "📊 *BOT MONITORING STATUS*\n\n"
                    f"📅 *Date:* `{state.get('date', 'N/A')}`\n"
                    f"⚡ *Signals Today:* {state.get('signals', 0)} / {config.MAX_TRADES_PER_DAY}\n"
                    f"🔍 *Last Scanned Candle:* `{state.get('last_scan', 'None')}`\n"
                    f"🔑 *Last Signal Key:* `{state.get('last_signal_key', 'None')}`"
                )
                send_message(reply, parse_mode="Markdown")

    except Exception as exc:
        print(f"[TELEGRAM CHECK ERROR] {exc}")

    return state
