import logging

from logging.handlers import TimedRotatingFileHandler

from src.core.config import LOG_PATH


FORMATTER = '%(asctime)s %(levelname)s %(name)s:\t%(message)s'


def get_file_handler():
    file_handler = TimedRotatingFileHandler(
        LOG_PATH,
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


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(get_file_handler())
logger.addHandler(get_stream_handler())
