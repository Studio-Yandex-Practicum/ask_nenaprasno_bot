import os
from pathlib import Path

from dotenv import dotenv_values

# This code is needed right here in order to import LOG_PATH into the logger. If this code is moved to config.py, then
# a cyclic import exception occurs.

BASE_DIR = Path(__file__).resolve().parent.parent

env = dotenv_values()


def get_string(setting: str) -> str:
    return env.get(setting) or os.getenv(setting)


LOG_NAME = get_string("LOG_NAME")
LOG_PATH = BASE_DIR / LOG_NAME
