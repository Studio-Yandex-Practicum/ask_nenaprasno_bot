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

TIME = datetime.time(hour=8, minute=5, second=00)
DAY = 16
WEEK_DAYS = (0,)
