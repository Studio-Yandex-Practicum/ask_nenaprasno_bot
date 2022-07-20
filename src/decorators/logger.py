# pylint: disable=W0703,E0401
from core.logger import logger


def async_error_logger(name):
    """Logs errors in wrapped asyc functions."""

    def log(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as err:
                logger.error("The error: %s after command: %s", str(err), name)

        return wrapper

    return log
