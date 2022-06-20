from pathlib import Path

from dotenv import dotenv_values

BASE_DIR = Path(__file__).parent.parent.parent

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

# -----------------------
# Logging settings
LOG_PATH = BASE_DIR / 'logs'
