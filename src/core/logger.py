import logging
from logging.handlers import TimedRotatingFileHandler

from core.config import LOG_LEVEL_STR, LOG_PATH

FORMATTER = "%(asctime)s %(levelname)s %(name)s:\t%(message)s"
LOG_LEVEL = logging.getLevelName(LOG_LEVEL_STR)


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_PATH, when="midnight", interval=1, encoding="utf-8", backupCount=14)
    formatter = logging.Formatter(FORMATTER)
    file_handler.setFormatter(formatter)
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(FORMATTER)
    stream_handler.setFormatter(formatter)
    return stream_handler


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(get_file_handler())
logger.addHandler(get_stream_handler())


async def log_response(response):
    request = response.request
    await response.aread()
    logger.debug("%s %s\nResponse: %s %s", request.method, request.url, response.status_code, response.text)
