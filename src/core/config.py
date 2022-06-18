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

WEEKLY_STAT_HOUR = int(env.get("WEEKLY_STAT_HOUR"))
WEEKLY_STAT_MINUTE = int(env.get("WEEKLY_STAT_MINUTE"))
WEEKLY_STAT_SECOND = int(env.get("WEEKLY_STAT_SECOND"))
WEEKLY_STAT_WEEK_DAYS = tuple(map(int, env.get("WEEKLY_STAT_WEEK_DAYS").split(",")))

MONTHLY_STAT_HOUR = int(env.get("MONTHLY_STAT_HOUR"))
MONTHLY_STAT_MINUTE = int(env.get("MONTHLY_STAT_MINUTE"))
MONTHLY_STAT_SECOND = int(env.get("MONTHLY_STAT_SECOND"))
MONTHLY_STAT_DAY = int(env.get("MONTHLY_STAT_DAY"))

RECEIPT_REMINDER_HOUR = int(env.get("RECEIPT_REMINDER_HOUR"))
RECEIPT_REMINDER_MINUTE = int(env.get("RECEIPT_REMINDER_MINUTE"))
RECEIPT_REMINDER_SECOND = int(env.get("RECEIPT_REMINDER_SECOND"))
RECEIPT_REMINDER_DAY = int(env.get("RECEIPT_REMINDER_DAY"))
# --------------------------------------------------------------------------------- #
