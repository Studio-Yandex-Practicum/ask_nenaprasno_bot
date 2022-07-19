# pylint: disable=W0703
from core.logger import logger


def async_error_logger(name):
    """Logs errors in wrapped asyc functions."""

    def log(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as err:
                error_message = f"The error: '{str(err)}' after command: '{name}'"
                logger.error(error_message)

        return wrapper

    return log
