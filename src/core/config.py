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


# Параметры логгера
LOG_NAME = get_string("LOG_NAME")
LOG_PATH = BASE_DIR / LOG_NAME

# Параметры локального сервера принимающего обновления от телеграм
HOST = get_string("HOST")
WEBHOOK_URL = get_string("WEBHOOK_URL")
PORT = get_int("BOT_PORT")
TOKEN = get_string("TELEGRAM_TOKEN")

# Параметры рассылки статистики
WEEKLY_STAT_TIME = get_datetime("WEEKLY_STAT_TIME")
WEEKLY_STAT_WEEK_DAYS = get_datetime_tuple(
    "WEEKLY_STAT_WEEK_DAYS"
)
MONTHLY_STAT_TIME = get_datetime("MONTHLY_STAT_TIME")
MONTHLY_STAT_DAY = get_int("MONTHLY_STAT_DAY")

# Параметры рассылки чеков
MONTHLY_RECEIPT_REMINDER_TIME = get_datetime(
    "MONTHLY_RECEIPT_REMINDER_TIME"
)
MONTHLY_RECEIPT_REMINDER_DAY = get_int("MONTHLY_RECEIPT_REMINDER_DAY")

# Файл с сохраненными данными бота
BOT_PERSISTENCE_FILE = get_string("BOT_PERSISTENCE_FILE")

# Настройка отладки
IS_FAKE_API = get_bool("IS_FAKE_API")

# Параметры api
SITE_API_URL = get_string("SITE_API_URL")
SITE_API_BOT_TOKEN = get_string("SITE_API_BOT_TOKEN")

# Параметры trello
TRELLO_API_KEY = get_string("TRELLO_API_KEY")
TRELLO_ID_MODEL = get_string("TRELLO_ID_MODEL")
TRELLO_TOKEN = get_string("TRELLO_TOKEN")
TRELLO_BORD_ID = get_string("TRELLO_BORD_ID")

# URL nenaprasno
URL_SITE = "https://ask.nenaprasno.ru/"
URL_SITE_DONATION = "https://ask.nenaprasno.ru/#donation"
FORM_URL_FUTURE_EXPERT = "https://forms.gle/DGMUm35bxZytE3QLA"
URL_SERVICE_RULES = "https://vse.nenaprasno.ru/rules"
