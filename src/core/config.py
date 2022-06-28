from datetime import datetime

from dotenv import dotenv_values

# ----------------------------------------------------------------------------------------------------- #
# Getting variables from .env                                                                           #
# ----------------------------------------------------------------------------------------------------- #
env = dotenv_values()

HOST = env.get("HOST")  # host для доступа к uvicorn серверу, по умолчанию localhost или 127.0.0.1
WEBHOOK_URL = env.get("WEBHOOK_URL")  # адрес сервера, где будет запущен бот
PORT = int(env.get("BOT_PORT"))  # port для доступа к uvicorn серверу, по умолчанию 8000
TOKEN = env.get("TELEGRAM_TOKEN")  # Токен телеграм бота

WEEKLY_STAT_TIME = datetime.strptime(env.get("WEEKLY_STAT_TIME"), "%H:%M")  # время еженельной статистики
WEEKLY_STAT_WEEK_DAYS = tuple(
    map(int, list(filter(None, env.get("WEEKLY_STAT_WEEK_DAYS").split(","))))
)  # дни недели для еженедельной статистики 0-6, где 0 - воскресенье

MONTHLY_STAT_TIME = datetime.strptime(env.get("MONTHLY_STAT_TIME"), "%H:%M")  # время ежемесячной статистики
MONTHLY_STAT_DAY = int(env.get("MONTHLY_STAT_DAY"))  # день для даты ежемесячной статистики

MONTHLY_RECEIPT_REMINDER_TIME = datetime.strptime(
    env.get("MONTHLY_RECEIPT_REMINDER_TIME"), "%H:%M"
)  # время для ежемесячного напоминания о чеке
MONTHLY_RECEIPT_REMINDER_DAY = int(
    env.get("MONTHLY_RECEIPT_REMINDER_DAY")
)  # день для даты ежемесячного напоминания о чеке

URL_SERVICE_RULES = env.get(
    "URL_SERVICE_RULES", "https://docs.google.com/document/d/1hW2HUv9aWQMnUBuIE_YQEtmIDDbk8KhpychckbyaIEQ/edit"
)

BOT_PERSISTENCE_FILE = env.get("BOT_PERSISTENCE_FILE")  # имя файла persistence бота
IS_FAKE_API = env.get("IS_FAKE_API")  # флаг, определяющий какой АПИ клиент используется - боевой или "заглушка"
SITE_API_URL = env.get("SITE_API_URL")  # адрес сервера, к которому будет отправлять запросы АПИ клиент
