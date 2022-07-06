from datetime import datetime
from pathlib import Path

from dotenv import dotenv_values

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------------- #
# Getting variables from .env                                                       #
# --------------------------------------------------------------------------------- #

env = dotenv_values()


def get_const_string(setting: str) -> str:
    return env.get(setting)


def get_const_int(setting: str) -> int:
    return int(env.get(setting))


def get_const_datetime(setting: str) -> datetime:
    return datetime.strptime(env.get(setting), "%H:%M")


def get_const_datetime_tuple(setting: str) -> tuple:
    return tuple(map(int, list(filter(None, env.get(setting).split(",")))))


def get_bool(setting: str):
    return env.get(setting)


LOG_NAME = get_const_string("LOG_NAME")
LOG_PATH = BASE_DIR / LOG_NAME

HOST = get_const_string("HOST")  # host для доступа к uvicorn серверу, по умолчанию localhost или 127.0.0.1
WEBHOOK_URL = get_const_string("WEBHOOK_URL")  # адрес сервера, где будет запущен бот

PORT = get_const_int("BOT_PORT")  # port для доступа к uvicorn серверу, по умолчанию 8000
TOKEN = get_const_string("TELEGRAM_TOKEN")  # Токен телеграм бота

WEEKLY_STAT_TIME = get_const_datetime("WEEKLY_STAT_TIME")  # время еженедельной статистики
WEEKLY_STAT_WEEK_DAYS = get_const_datetime_tuple(
    "WEEKLY_STAT_WEEK_DAYS"
)  # дни недели для еженедельной статистики 0-6, где 0 - воскресенье

MONTHLY_STAT_TIME = get_const_datetime("MONTHLY_STAT_TIME")  # время ежемесячной статистики
MONTHLY_STAT_DAY = get_const_int("MONTHLY_STAT_DAY")  # день для даты ежемесячной статистики

MONTHLY_RECEIPT_REMINDER_TIME = get_const_datetime(
    "MONTHLY_RECEIPT_REMINDER_TIME"
)  # время для ежемесячного напоминания о чеке
MONTHLY_RECEIPT_REMINDER_DAY = get_const_int(
    "MONTHLY_RECEIPT_REMINDER_DAY"
)  # день для даты ежемесячного напоминания о чеке

URL_SERVICE_RULES = get_const_string("URL_SERVICE_RULES")

BOT_PERSISTENCE_FILE = get_const_string("BOT_PERSISTENCE_FILE")  # имя файла persistence бота
IS_FAKE_API = get_bool(
    "IS_FAKE_API"
)  # флаг, определяющий какой АПИ клиент используется - боевой или "заглушка"
SITE_API_URL = get_const_string("SITE_API_URL")  # адрес сервера, к которому будет отправлять запросы АПИ клиент

TRELLO_API_KEY = get_const_string("TRELLO_API_KEY")  # API ключ разработчика
TRELLO_ID_MODEL = get_const_string("TRELLO_ID_MODEL")  # id таблицы, к которой будет привязан webhook
TRELLO_TOKEN = get_const_string("TRELLO_TOKEN")  # токен для доступа к TRELLO
