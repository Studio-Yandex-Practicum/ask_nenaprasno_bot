import logging
from logging.handlers import TimedRotatingFileHandler

from src.core.config import LOG_PATH, LOG_FILE


FORMATTER = '%(asctime)s %(levelname)s %(name)s:\t%(message)s'


def get_file_handler():
    file_handler = TimedRotatingFileHandler(
        LOG_FILE,
        when='midnight',
        interval=1,
        encoding='utf-8',
        backupCount=14
    )
    formatter = logging.Formatter(FORMATTER)
    file_handler.setFormatter(formatter)
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(FORMATTER)
    stream_handler.setFormatter(formatter)
    return stream_handler


def bot_logging():
    bot_logger = logging.getLogger('Bot')  # noqa
    bot_logger.setLevel(logging.INFO)
    bot_logger.addHandler(get_file_handler())
    bot_logger.addHandler(get_stream_handler())
    return bot_logger


LOG_PATH.mkdir(exist_ok=True)
logger = bot_logging()
