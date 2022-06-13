from dotenv import load_dotenv, dotenv_values
from pathlib import Path
from pydantic import (BaseSettings, HttpUrl, IPvAnyAddress)

BASE_DIR = Path(__name__).resolve().parent.parent.parent
# --------------------------------------------------------------------------------- #
# Getting variables from .env                                                       #
# --------------------------------------------------------------------------------- #
load_dotenv()


class Settings(BaseSettings):
    host: str
    webhook_url: HttpUrl
    port: int
    token: str
    webhook_ip: str

    class Config:
        fields = {"port": {"env": "bot_port"}, "token": {"env": "telegram_token"}}


HOST = (s := Settings()).host
WEBHOOK_URL = s.webhook_url
PORT = s.port
TOKEN = s.token
WEBHOOK_IP = s.webhook_ip
# --------------------------------------------------------------------------------- #
