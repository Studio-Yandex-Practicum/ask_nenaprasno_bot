import os
from pathlib import Path
from datetime import datetime
from dotenv import dotenv_values

BASE_DIR = Path(__file__).parent.parent.parent
LOG_PATH = BASE_DIR / 'logs'
LOG_FILE = os.path.join(LOG_PATH, 'bot-log.txt')

# --------------------------------------------------------------------------------- #
# Getting variables from .env                                                       #
# --------------------------------------------------------------------------------- #

env = dotenv_values()

HOST = env.get("HOST")
WEBHOOK_URL = env.get("WEBHOOK_URL")
PORT = int(env.get("BOT_PORT"))
TOKEN = env.get("TELEGRAM_TOKEN")

CHAT_ID = env.get("CHAT_ID")
TEST_PERIOD = int(env.get("TEST_PERIOD"))

WEEKLY_STAT_TIME = datetime.strptime(env.get("WEEKLY_STAT_TIME"), "%H:%M")
WEEKLY_STAT_WEEK_DAYS = tuple(map(int, list(filter(None, env.get("WEEKLY_STAT_WEEK_DAYS").split(",")))))

MONTHLY_STAT_TIME = datetime.strptime(env.get("MONTHLY_STAT_TIME"), "%H:%M")
MONTHLY_STAT_DAY = int(env.get("MONTHLY_STAT_DAY"))

MONTHLY_RECEIPT_REMINDER_TIME = datetime.strptime(env.get("MONTHLY_RECEIPT_REMINDER_TIME"), "%H:%M")
MONTHLY_RECEIPT_REMINDER_DAY = int(env.get("MONTHLY_RECEIPT_REMINDER_DAY"))
# -------------------------------------------------------------------------------------------------- #
URL_SERVICE_RULES = "https://docs.google.com/document/d/1hW2HUv9aWQMnUBuIE_YQEtmIDDbk8KhpychckbyaIEQ/edit"
# -------------------------------------------------------------------------------------------------- #
BOT_PERSISTENCE_FILE = env.get("BOT_PERSISTENCE_FILE")
FAKE_API = env.get("FAKE_API")
