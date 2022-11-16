import logging
from logging import config as logging_config

from core import config as bot_config

FORMATTER = "%(asctime)s %(levelname)s %(name)s:\t%(message)s"
LOG_LEVEL = logging.getLevelName(bot_config.LOG_LEVEL_STR)
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": FORMATTER,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s %(levelname)s %(name)s:\t%(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "default",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": bot_config.LOG_PATH,
            "when": "midnight",
            "interval": 1,
            "encoding": "utf-8",
            "backupCount": 14,
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn.error": {"handlers": ["default", "file"], "level": "ERROR"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        __name__: {"handlers": ["default", "file"], "level": LOG_LEVEL},
    },
}


logging_config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


async def log_response(response):
    request = response.request
    await response.aread()
    logger.debug("%s %s\nResponse: %s %s", request.method, request.url, response.status_code, response.text)
