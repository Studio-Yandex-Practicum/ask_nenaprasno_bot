from datetime import datetime
from pathlib import Path

from dotenv import dotenv_values

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------------- #
# Getting variables from .env                                                       #
# --------------------------------------------------------------------------------- #

env = dotenv_values()


def get_string(setting: str) -> str:
    """Получить строковое значение из .env файла."""
    return env.get(setting)


def get_int(setting: str) -> int:
    """Получить числовое значение из .env файла."""
    return int(env.get(setting))


def get_datetime(setting: str) -> datetime:
    """Получить значение datetime из .env файла."""
    return datetime.strptime(env.get(setting), "%H:%M")


def get_datetime_tuple(setting: str) -> tuple:
    """Получить кортеж datetime из .env файла."""
    return tuple(map(int, list(filter(None, env.get(setting).split(",")))))


def get_bool(setting: str) -> bool:
    """Получить булевое значение из .env файла."""
    return env.get(setting) == "True"


# название логера для бота (по умолчанию None)
LOG_NAME = get_string("LOG_NAME")
# путь до логера
LOG_PATH = BASE_DIR / LOG_NAME

# host для доступа к uvicorn серверу, по умолчанию localhost или 127.0.0.1
HOST = get_string("HOST")
# адрес сервера, где будет запущен бот
WEBHOOK_URL = get_string("WEBHOOK_URL")

# port для доступа к uvicorn серверу, по умолчанию 8000
PORT = get_int("BOT_PORT")
# Токен телеграм бота
TOKEN = get_string("TELEGRAM_TOKEN")

# время еженедельной статистики
WEEKLY_STAT_TIME = get_datetime("WEEKLY_STAT_TIME")
# дни недели для еженедельной статистики 0-6, где 0 - воскресенье
WEEKLY_STAT_WEEK_DAYS = get_datetime_tuple(
    "WEEKLY_STAT_WEEK_DAYS"
)

# время ежемесячной статистики
MONTHLY_STAT_TIME = get_datetime("MONTHLY_STAT_TIME")
# день для даты ежемесячной статистики
MONTHLY_STAT_DAY = get_int("MONTHLY_STAT_DAY")

# время для ежемесячного напоминания о чеке
MONTHLY_RECEIPT_REMINDER_TIME = get_datetime(
    "MONTHLY_RECEIPT_REMINDER_TIME"
)
# день для даты ежемесячного напоминания о чеке
MONTHLY_RECEIPT_REMINDER_DAY = get_int("MONTHLY_RECEIPT_REMINDER_DAY")

# имя файла persistence бота
BOT_PERSISTENCE_FILE = get_string("BOT_PERSISTENCE_FILE")
# флаг, определяющий какой АПИ клиент используется - боевой или "заглушка"
IS_FAKE_API = get_bool("IS_FAKE_API")
# адрес сервера, к которому будет отправлять запросы АПИ клиент
SITE_API_URL = get_string("SITE_API_URL")
# токен для сайта
SITE_API_BOT_TOKEN = get_string("SITE_API_BOT_TOKEN")

# API ключ разработчика
TRELLO_API_KEY = get_string("TRELLO_API_KEY")
# id таблицы, к которой будет привязан webhook
TRELLO_ID_MODEL = get_string("TRELLO_ID_MODEL")
# токен для доступа к TRELLO
TRELLO_TOKEN = get_string("TRELLO_TOKEN")
# доска в TRELLO
TRELLO_BORD_ID = get_string("TRELLO_BORD_ID")

# сайт проекта не напрасно
URL_SITE = "https://ask.nenaprasno.ru/"
# ссылка для отправки пожертвований
URL_SITE_DONATION = "https://ask.nenaprasno.ru/#donation"

# ссылка на анкету для регистрации новых экспертов
FORM_URL_FUTURE_EXPERT = "https://forms.gle/DGMUm35bxZytE3QLA"
# адрес страницы с правилами
URL_SERVICE_RULES = "https://vse.nenaprasno.ru/rules"
