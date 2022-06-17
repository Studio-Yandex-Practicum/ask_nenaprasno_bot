import datetime

from dotenv import dotenv_values

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
# --------------------------------------------------------------------------------- #

WEEKLY_STAT_TIME = datetime.time(hour=11, minute=34, second=00)
WEEKLY_STAT_WEEK_DAYS = (0,)

MONTHLY_STAT_TIME = datetime.time(hour=11, minute=34, second=00)
MONTHLY_STAT_DAY = 17

RECEIPT_REMINDER_TIME = datetime.time(hour=11, minute=34, second=00)
RECEIPT_REMINDER_DAY = 31
