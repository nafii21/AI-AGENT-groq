import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("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", "")
TWELVE_DATA_API_KEY = os.getenv("593b71515ffe46949594924edbc952e6", "")
TELEGRAM_BOT_TOKEN = os.getenv("8806108760:AAF7NJUz1I3unPAMg7v5hSvAlAJ34PYi5G4", "")
TELEGRAM_CHAT_ID = os.getenv("6273206309", "")

SYMBOL = os.getenv("SYMBOL", "XAU/USD")
TIMEZONE = os.getenv("TIMEZONE", "UTC")

DAILY_LOOKBACK = int(os.getenv("DAILY_LOOKBACK", "80"))
M15_LOOKBACK = int(os.getenv("M15_LOOKBACK", "50"))
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "60"))
POI_TOLERANCE = float(os.getenv("POI_TOLERANCE", "0.001"))
MAX_TRADES_PER_DAY = int(os.getenv("MAX_TRADES_PER_DAY", "2"))

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
MIN_AI_CONFIDENCE = int(os.getenv("MIN_AI_CONFIDENCE", "70"))

OB_ATR_PERIOD = int(os.getenv("OB_ATR_PERIOD", "14"))
OB_DISPLACEMENT_ATR = float(os.getenv("OB_DISPLACEMENT_ATR", "1.2"))
