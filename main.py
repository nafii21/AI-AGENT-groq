import time
import traceback
import pandas as pd

import config
from core.market_data import get_daily, get_m15, latest_closed_m15
from core.daily_poi import build_pois, price_in_poi
from core.engulfing import detect
from core.ai_agent import validate_setup
from core.state import load_state, save_state, reset_if_new_day
from telegram.bot import send_message, process_incoming_updates

def fmt(x):
    return f"{float(x):.2f}"

def format_signal(setup, ai):
    p = setup["poi"]
    e = setup["engulfing"]
    c = e["candle"]
    direction = ai["direction"]

    return (
        f"📊 XAU/USD | M15 SETUP\n\n"
        f"📍 DAILY POI\n"
        f"{p['kind']} | {p['direction']}\n"
        f"Zone: {fmt(p['low'])} - {fmt(p['high'])}\n"
        f"Source: {p['source_time']}\n\n"
        f"📈 PRICE ACTION\n"
        f"{e['type']}\n"
        f"M15 close: {fmt(c['close'])}\n"
        f"Candle: {c['datetime']}\n\n"
        f"🧠 AI VALIDATION\n"
        f"Decision: {ai['decision']}\n"
        f"Direction: {direction}\n"
        f"Confidence: {ai['confidence']}%\n"
        f"Reason: {ai['reason']}\n"
        f"Risk: {ai['risk_note']}\n\n"
        f"Signals today: {setup['signals_today']}/{config.MAX_TRADES_PER_DAY}"
    )

def scan_once(state):
    daily = get_daily()
    pois = build_pois(daily)

    m15 = get_m15()
    
    # Pastikan format UTC konsisten untuk mencegah perbandingan tz-naive vs tz-aware
    m15["datetime"] = pd.to_datetime(m15["datetime"], utc=True)
    now_utc = pd.Timestamp.now(tz="UTC")
    closed = m15[m15["datetime"] + pd.Timedelta(minutes=15) <= now_utc].copy()
    
    if len(closed) < 2:
        return state

    latest = closed.iloc[-1]
    price = float(latest["close"])

    active = [p for p in pois if price_in_poi(price, p)]
    if not active:
        state["last_scan"] = str(latest["datetime"])
        save_state(state)
        return state

    engulf = detect(closed)
    if not engulf:
        state["last_scan"] = str(latest["datetime"])
        save_state(state)
        return state

    if state["signals"] >= config.MAX_TRADES_PER_DAY:
        return state

    candle_time = str(engulf["candle"]["datetime"])
    signal_key = f"{state['date']}|{candle_time}|{engulf['type']}"
    if signal_key == state.get("last_signal_key"):
        return state

    poi = active[0]

    # Direction coherence check sebelum konsumsi token Groq
    expected = "BUY" if poi.direction == "BULLISH" else "SELL"
    detected_direction = "BUY" if engulf["type"] == "BULLISH_ENGULFING" else "SELL"
    if expected != detected_direction:
        state["last_signal_key"] = signal_key
        state["last_scan"] = candle_time
        save_state(state)
        return state

    setup = {
        "symbol": config.SYMBOL,
        "strategy": "DAILY_POI_PLUS_M15_ENGULFING",
        "poi": poi.to_dict(),
        "engulfing": {
            "type": engulf["type"],
            "candle": {
                "datetime": str(engulf["candle"]["datetime"]),
                "open": float(engulf["candle"]["open"]),
                "high": float(engulf["candle"]["high"]),
                "low": float(engulf["candle"]["low"]),
                "close": float(engulf["candle"]["close"]),
            },
            "previous": {
                "open": float(engulf["previous"]["open"]),
                "high": float(engulf["previous"]["high"]),
                "low": float(engulf["previous"]["low"]),
                "close": float(engulf["previous"]["close"]),
            },
        },
        "signals_today": state["signals"] + 1,
    }

    ai = validate_setup(setup)

    state["last_signal_key"] = signal_key
    state["last_scan"] = candle_time

    if ai["decision"] == "VALID" and ai["confidence"] >= config.MIN_AI_CONFIDENCE:
        state["signals"] += 1
        setup["signals_today"] = state["signals"]
        send_message(format_signal(setup, ai))
    else:
        send_message(
            f"❌ XAU/USD | SETUP REJECTED\n"
            f"POI: {poi.kind} {poi.direction}\n"
            f"PA: {engulf['type']}\n"
            f"AI: {ai['decision']} | {ai['confidence']}%\n"
            f"Reason: {ai['reason']}"
        )

    save_state(state)
    return state

def validate_env():
    missing = []
    for name, value in [
        ("GROQ_API_KEY", config.GROQ_API_KEY),
        ("TWELVE_DATA_API_KEY", config.TWELVE_DATA_API_KEY),
        ("TELEGRAM_BOT_TOKEN", config.TELEGRAM_BOT_TOKEN),
        ("TELEGRAM_CHAT_ID", config.TELEGRAM_CHAT_ID),
    ]:
        if not value:
            missing.append(name)
    if missing:
        raise RuntimeError("Missing environment variables: " + ", ".join(missing))

def main():
    validate_env()
    print("AI Trading Agent V1 started.")
    state = reset_if_new_day(load_state())
    save_state(state)

    while True:
        try:
            state = reset_if_new_day(state)
            
            # 1. Cek & respon perintah dari Telegram (/start atau /status)
            state = process_incoming_updates(state)
            
            # 2. Jalankan scanner strategi & AI
            state = scan_once(state)
            
            save_state(state)
        except Exception as exc:
            print(f"[ERROR] {exc}")
            traceback.print_exc()
        time.sleep(config.POLL_SECONDS)

if __name__ == "__main__":
    main()
