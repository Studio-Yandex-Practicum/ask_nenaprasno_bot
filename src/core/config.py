from datetime import time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).resolve().parent.parent

# Параметры общей папки с данными
DATA_PATH = BASE_DIR.parent / ".data"

# Параметры логгера
logs_folder = DATA_PATH / "logs"
logs_folder.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    # Токен телеграм бота
    telegram_token: str
    # адрес сервера, где будет запущен бот
    application_url: str
    # host для доступа к uvicorn серверу, по умолчанию localhost или 127.0.0.1
    host: str = "0.0.0.0"
    # Токен, с которым телеграм будет обращаться к боту. Допускаются только символы A-Z, a-z, 0-9, _, -
    secret_telegram_token: str

    # время еженедельной статистики
    weekly_stat_time: time
    # дни недели для еженедельной статистики 0-6, где 0 - воскресенье
    weekly_stat_week_days: int = 0

    # время ежемесячной статистики
    monthly_stat_time: time
    # день для даты ежемесячной статистики
    monthly_stat_day: int = 1

    # время для ежемесячного напоминания о чеке
    monthly_receipt_reminder_time: time
    # день для даты ежемесячного напоминания о чеке
    monthly_receipt_reminder_day: int

    # время ежедневного получения напоминаний о просроченных заявках
    daily_consultations_reminder_time: time

    # Токен(uuid) для идентификации бота на сайте.
    site_api_bot_token: str
    # адрес сервера, к которому будет отправлять запросы API клиент
    url_ask_nenaprasno_api: str
    # главный url nenaprasno
    url_ask_nenaprasno: str
    # флаг, определяющий какой АПИ клиент используется - боевой или "заглушка", отдающая фейковые данные
    is_fake_api: bool = False

    # Уровень записи логов
    log_level: str = "INFO"

    # доска в TRELLO
    trello_bord_id: str

    # статичные значения
    port: int = Field(8000)
    form_url_future_expert: str = Field("https://forms.gle/DGMUm35bxZytE3QLA")
    url_service_rules: str = Field(
        "https://docs.google.com/document/d/1hW2HUv9aWQMnUBuIE_YQEtmIDDbk8KhpychckbyaIEQ/edit"
    )
    bot_persistence_file: Path = Field(DATA_PATH / "bot_persistence_file")
    stat_collection_time: time = Field(time(tzinfo=ZoneInfo("Asia/Kamchatka")))
    log_path: Path = Field(logs_folder / "bot.log")
    daily_collect_consultation_time: time = Field(time(tzinfo=timezone.utc))

    class Config:  # pylint: disable=R0903
        env_file = BASE_DIR.parent / ".env"


settings = Settings()
