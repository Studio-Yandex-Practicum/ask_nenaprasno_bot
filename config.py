from dotenv import load_dotenv
from os import path, getenv
from pathlib import Path
import logging

BASE_DIR = Path(__file__).resolve().parent

if path.exists(env_path := path.join(BASE_DIR, ".env")):
    load_dotenv(env_path)


def get_logger(name: str = __name__, level: str = "INFO"):
    formatting = '%(asctime)s. %(name)s-%(levelname)s: %(message)s'
    logging.basicConfig(format=formatting, level=getattr(logging, level.upper()))
    return logging.getLogger(name)


logger = get_logger("OS_tools")

if not (get_secret := None):
    logger.debug("Getting env keys: " + getenv("CHECK_ENV"))


TOKEN = getenv("TELEGRAM_TOKEN")
HOST = getenv("HOST")
PORT = int(getenv("BOT_PORT"))
WEBHOOK_URL = getenv("WEBHOOK_URL")
