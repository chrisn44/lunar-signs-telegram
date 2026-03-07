import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ADMIN_IDS = [int(id_) for id_ in os.getenv("ADMIN_IDS", "").split(",") if id_]

# Premium prices (Telegram Stars)
PREMIUM_WEEK_STARS = 50
PREMIUM_MONTH_STARS = 150

# Horoscope API
AZTRO_API_URL = "https://aztro.sameerkumar.herokuapp.com/"

# Rate limits
RATE_LIMIT_PER_MINUTE = 5
RATE_LIMIT_PER_DAY = 20