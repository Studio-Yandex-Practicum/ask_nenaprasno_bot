# pylint: disable=W0703
from core.logger import logger


def async_error_logger(name):
    """Logs errors in wrapped asyc functions."""

    def log(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception:
                logger.exception("The error after command: %s", name)

        return wrapper

    return log
