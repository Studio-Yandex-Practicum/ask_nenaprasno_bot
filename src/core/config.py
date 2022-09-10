import os
from datetime import datetime, time, timezone
from pathlib import Path

from dotenv import dotenv_values

from decorators.safe_conversion import safe_conversion

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------------- #
# Getting variables from .env                                                       #
# --------------------------------------------------------------------------------- #

env = dotenv_values()


def get_string(setting: str) -> str:
    return env.get(setting) or os.getenv(setting)


@safe_conversion
def get_int(setting: str) -> int:
    return int(get_string(setting))


@safe_conversion
def get_datetime(setting: str) -> datetime:
    return datetime.strptime(get_string(setting), "%H:%M")


@safe_conversion
def get_time(setting: str) -> time:
    return get_datetime(setting).time()


@safe_conversion
def get_datetime_tuple(setting: str) -> tuple:
    return tuple(map(int, list(filter(None, get_string(setting).split(",")))))


def get_bool(setting: str) -> bool:
    return get_string(setting) == "True"


# Параметры логгера
LOG_NAME = get_string("LOG_NAME")
LOG_PATH = BASE_DIR / "logs" / LOG_NAME

# Параметры локального сервера принимающего обновления от телеграм
HOST = get_string("HOST")
WEBHOOK_URL = get_string("WEBHOOK_URL")
PORT = get_int("BOT_PORT")
TOKEN = get_string("TELEGRAM_TOKEN")

# Параметры для аутентификации телеграма
SECRET_TELEGRAM_TOKEN = get_string("SECRET_TELEGRAM_TOKEN")

# Параметры рассылки статистики
WEEKLY_STAT_TIME = get_time("WEEKLY_STAT_TIME")
WEEKLY_STAT_WEEK_DAYS = get_datetime_tuple("WEEKLY_STAT_WEEK_DAYS")
MONTHLY_STAT_TIME = get_time("MONTHLY_STAT_TIME")
MONTHLY_STAT_DAY = get_int("MONTHLY_STAT_DAY")

# Параметры рассылки чеков
MONTHLY_RECEIPT_REMINDER_TIME = get_datetime("MONTHLY_RECEIPT_REMINDER_TIME")
MONTHLY_RECEIPT_REMINDER_DAY = get_int("MONTHLY_RECEIPT_REMINDER_DAY")

# Параметры рассылки напоминаний
DAILY_COLLECT_CONSULTATIONS_TIME = time(hour=0, minute=0, tzinfo=timezone.utc)
DAILY_CONSULTATIONS_REMINDER_TIME = get_time("DAILY_CONSULTATIONS_REMINDER_TIME")

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
FORM_URL_FUTURE_EXPERT = "https://forms.gle/DGMUm35bxZytE3QLA"
URL_SERVICE_RULES = "https://docs.google.com/document/d/1hW2HUv9aWQMnUBuIE_YQEtmIDDbk8KhpychckbyaIEQ/edit"
URL_ASK_NENAPRASNO = get_string("URL_ASK_NENAPRASNO")
