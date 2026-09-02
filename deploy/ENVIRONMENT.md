# Deployment checklist

Set these environment variables in your deployment platform:

GROQ_API_KEY
TWELVE_DATA_API_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID

Optional:
SYMBOL
TIMEZONE
DAILY_LOOKBACK
M15_LOOKBACK
POLL_SECONDS
POI_TOLERANCE
MAX_TRADES_PER_DAY
GROQ_MODEL
MIN_AI_CONFIDENCE
OB_ATR_PERIOD
OB_DISPLACEMENT_ATR

Start command:

python main.py

The service must support a persistent worker/background process.
