from dotenv import dotenv_values

# --------------------------------------------------------------------------------- #
# Getting variables from .env                                                       #
# --------------------------------------------------------------------------------- #
env = dotenv_values()

HOST = env.get("HOST")
WEBHOOK_URL = env.get("WEBHOOK_URL")
PORT = int(env.get("BOT_PORT"))
TOKEN = env.get("TELEGRAM_TOKEN")
WEBHOOK_IP = env.get("WEBHOOK_IP")
CHAT_ID = env.get("CHAT_ID")
TEST_PERIOD = int(env.get("TEST_PERIOD"))
# --------------------------------------------------------------------------------- #
