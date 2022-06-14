from dotenv import dotenv_values

# --------------------------------------------------------------------------------- #
# Getting variables from .env                                                       #
# --------------------------------------------------------------------------------- #
ENVS = dotenv_values()

HOST = ENVS["HOST"]
WEBHOOK_URL = ENVS["WEBHOOK_URL"]
PORT = int(ENVS["BOT_PORT"])
TOKEN = ENVS["TELEGRAM_TOKEN"]
WEBHOOK_IP = ENVS["WEBHOOK_IP"]
CHAT_ID = ENVS["CHAT_ID"]
TEST_PERIOD = int(ENVS["TEST_PERIOD"])
# --------------------------------------------------------------------------------- #
