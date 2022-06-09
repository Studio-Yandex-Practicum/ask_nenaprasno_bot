from dotenv import load_dotenv
from os import path, getenv
from pathlib import Path

from logger import get_logger

BASE_DIR = Path(__file__).resolve().parent.parent

if path.exists(env_path := path.join(BASE_DIR, ".env")):
    load_dotenv(env_path)

logger = get_logger("OS_tools")

if not (get_secret := None):
    get_secret = getenv
    logger.debug("Getting env keys: " + get_secret("CHECK_ENV"))
