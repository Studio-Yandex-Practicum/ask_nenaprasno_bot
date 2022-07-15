import os
from pathlib import Path

from dotenv import dotenv_values

BASE_DIR = Path(__file__).resolve().parent.parent

env = dotenv_values()


def get_string(setting: str) -> str:
    return env.get(setting) or os.getenv(setting)


LOG_NAME = get_string("LOG_NAME")
LOG_PATH = BASE_DIR / LOG_NAME
