from datetime import datetime
from pathlib import Path

from dotenv import dotenv_values

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------------- #
# Getting variables from .env                                                       #
# --------------------------------------------------------------------------------- #

env = dotenv_values()


def get_string(setting: str) -> str:
    return env.get(setting)


def get_int(setting: str) -> int:
    return int(env.get(setting))


def get_datetime(setting: str) -> datetime:
    return datetime.strptime(env.get(setting), "%H:%M")


def get_datetime_tuple(setting: str) -> tuple:
    return tuple(map(int, list(filter(None, env.get(setting).split(",")))))


def get_bool(setting: str) -> bool:
    return env.get(setting) == "True"


LOG_NAME = get_string("LOG_NAME")
LOG_PATH = BASE_DIR / LOG_NAME

HOST = get_string("HOST")  # host для доступа к uvicorn серверу, по умолчанию localhost или 127.0.0.1
WEBHOOK_URL = get_string("WEBHOOK_URL")  # адрес сервера, где будет запущен бот

PORT = get_int("BOT_PORT")  # port для доступа к uvicorn серверу, по умолчанию 8000
TOKEN = get_string("TELEGRAM_TOKEN")  # Токен телеграм бота

WEEKLY_STAT_TIME = get_datetime("WEEKLY_STAT_TIME")  # время еженедельной статистики
WEEKLY_STAT_WEEK_DAYS = get_datetime_tuple(
    "WEEKLY_STAT_WEEK_DAYS"
)  # дни недели для еженедельной статистики 0-6, где 0 - воскресенье

MONTHLY_STAT_TIME = get_datetime("MONTHLY_STAT_TIME")  # время ежемесячной статистики
MONTHLY_STAT_DAY = get_int("MONTHLY_STAT_DAY")  # день для даты ежемесячной статистики

MONTHLY_RECEIPT_REMINDER_TIME = get_datetime(
    "MONTHLY_RECEIPT_REMINDER_TIME"
)  # время для ежемесячного напоминания о чеке
MONTHLY_RECEIPT_REMINDER_DAY = get_int("MONTHLY_RECEIPT_REMINDER_DAY")  # день для даты ежемесячного напоминания о чеке

URL_SERVICE_RULES = get_string("URL_SERVICE_RULES")

BOT_PERSISTENCE_FILE = get_string("BOT_PERSISTENCE_FILE")  # имя файла persistence бота
IS_FAKE_API = get_bool("IS_FAKE_API")  # флаг, определяющий какой АПИ клиент используется - боевой или "заглушка"
SITE_API_URL = get_string("SITE_API_URL")  # адрес сервера, к которому будет отправлять запросы АПИ клиент
SITE_API_BOT_TOKEN = get_string("SITE_API_BOT_TOKEN")

TRELLO_API_KEY = get_string("TRELLO_API_KEY")  # API ключ разработчика
TRELLO_ID_MODEL = get_string("TRELLO_ID_MODEL")  # id таблицы, к которой будет привязан webhook
TRELLO_TOKEN = get_string("TRELLO_TOKEN")  # токен для доступа к TRELLO
TRELLO_BORD_ID = get_string("TRELLO_BORD_ID")  # доска в TRELLO
