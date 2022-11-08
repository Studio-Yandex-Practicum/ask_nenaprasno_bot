import os
from datetime import datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import dotenv_values

from decorators.safe_conversion import safe_conversion

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------------- #
# Getting variables from .env                                                       #
# --------------------------------------------------------------------------------- #

env = dotenv_values()


def get_string(setting: str, default: str = None) -> str:
    return env.get(setting) or os.getenv(setting, default)


@safe_conversion
def get_int(setting: str, default: str = None) -> int:
    return int(get_string(setting, default))


@safe_conversion
def get_datetime(setting: str, default: str = None) -> datetime:
    return datetime.strptime(get_string(setting, default), "%H:%M")


@safe_conversion
def get_time(setting: str, default: str = None) -> time:
    return get_datetime(setting, default).time()


@safe_conversion
def get_datetime_tuple(setting: str, default: str = None) -> tuple:
    return tuple(map(int, list(filter(None, get_string(setting, default).split(",")))))


def get_bool(setting: str, default: str = "False") -> bool:
    return get_string(setting, default) == "True"


# Параметры общей папки с данными
DATA_PATH = BASE_DIR.parent / ".data"

# Параметры логгера
Path(DATA_PATH / "logs").mkdir(parents=True, exist_ok=True)
LOG_PATH = DATA_PATH / "logs" / "bot.log"

# Параметры локального сервера принимающего обновления от телеграм
HOST = get_string("HOST", "0.0.0.0")
APPLICATION_URL = get_string("APPLICATION_URL")

PORT = 8000

TOKEN = get_string("TELEGRAM_TOKEN")

# Параметры для аутентификации телеграма
SECRET_TELEGRAM_TOKEN = get_string("SECRET_TELEGRAM_TOKEN")

# Параметры рассылки статистики
WEEKLY_STAT_TIME = get_time("WEEKLY_STAT_TIME", "10:00")
WEEKLY_STAT_WEEK_DAYS = get_datetime_tuple("WEEKLY_STAT_WEEK_DAYS", "0")
MONTHLY_STAT_TIME = get_time("MONTHLY_STAT_TIME", "11:00")
MONTHLY_STAT_DAY = get_int("MONTHLY_STAT_DAY", "28")

# Параметры рассылки чеков
MONTHLY_RECEIPT_REMINDER_TIME = get_datetime("MONTHLY_RECEIPT_REMINDER_TIME", "12:00")
MONTHLY_RECEIPT_REMINDER_DAY = get_int("MONTHLY_RECEIPT_REMINDER_DAY", "20")

# Параметры рассылки напоминаний
DAILY_COLLECT_CONSULTATIONS_TIME = time(hour=0, minute=0, tzinfo=timezone.utc)
DAILY_CONSULTATIONS_REMINDER_TIME = get_time("DAILY_CONSULTATIONS_REMINDER_TIME", "17:00")

# Параметры запуска сбора недельной и месячной статистики - по умолчанию, полночь GTM+12
__collect_time = get_time("STAT_COLLECTION_TIME", "00:00")
STAT_COLLECTION_TIMEZONE = "Asia/Kamchatka"
# STAT_COLLECTION_TIME = time(hour=0, minute=0, second=0, tzinfo=ZoneInfo(STAT_COLLECTION_TIMEZONE))
STAT_COLLECTION_TIME = __collect_time.replace(tzinfo=ZoneInfo(STAT_COLLECTION_TIMEZONE))

# Файл с сохраненными данными бота
BOT_PERSISTENCE_FILE = DATA_PATH / "bot_persistence_file"

# Настройка отладки
IS_FAKE_API = get_bool("IS_FAKE_API", "False")

# Параметры trello
TRELLO_BORD_ID = get_string("TRELLO_BORD_ID")

# Параметры внешнего api
URL_ASK_NENAPRASNO_API = get_string("URL_ASK_NENAPRASNO_API")
SITE_API_BOT_TOKEN = get_string("SITE_API_BOT_TOKEN")

# URL nenaprasno
FORM_URL_FUTURE_EXPERT = "https://forms.gle/DGMUm35bxZytE3QLA"
URL_SERVICE_RULES = "https://docs.google.com/document/d/1hW2HUv9aWQMnUBuIE_YQEtmIDDbk8KhpychckbyaIEQ/edit"
URL_ASK_NENAPRASNO = get_string("URL_ASK_NENAPRASNO")

# Включить debug-режим
DEBUG = get_bool("DEBUG")
