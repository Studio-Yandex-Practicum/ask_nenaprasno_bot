import logging
from logging.handlers import TimedRotatingFileHandler

from src.core.config import LOG_PATH


FORMATTER = u'%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s'


def get_file_handler(path_name):
    file_handler = TimedRotatingFileHandler(
        f'{LOG_PATH}/{path_name}',
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
    bot_file_handler = get_file_handler('bot_logs.txt')
    bot_logger.addHandler(bot_file_handler)
    bot_stream_handler = get_stream_handler()
    bot_logger.addHandler(bot_stream_handler)
    return bot_logger


def webhook_logging():
    webhook_logger = logging.getLogger('Webhook')  # noqa
    webhook_logger.setLevel(logging.INFO)
    webhook_file_handler = get_file_handler('webhook.txt')
    webhook_logger.addHandler(webhook_file_handler)
    webhook_stream_handler = get_stream_handler()
    webhook_logger.addHandler(webhook_stream_handler)
    return webhook_logger


LOG_PATH.mkdir(exist_ok=True)
bot_logger = bot_logging()
webhook_logger = webhook_logging()
