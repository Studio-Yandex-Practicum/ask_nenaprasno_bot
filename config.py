from dotenv import dotenv_values
from pathlib import Path

BASE_DIR = Path(__name__).resolve().parent

# ---------------------------------------- #
# Getting variables from .env              #
# ---------------------------------------- #
VARS = dotenv_values(BASE_DIR/".env")

HOST = dotenv_values()["HOST"]
PORT = int(VARS["BOT_PORT"])
TOKEN = VARS["TELEGRAM_TOKEN"]
WEBHOOK_URL = VARS["WEBHOOK_URL"]
# ---------------------------------------- #
