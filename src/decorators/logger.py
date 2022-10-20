# pylint: disable=W0703
import functools
from typing import Callable

from core.logger import logger


def async_error_logger(name):
    """Logs errors in wrapped async functions."""

    def log(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            update = args[0]
            try:
                logger.debug("User %s run %s", update.effective_user.id, func.__name__)
                return await func(*args, **kwargs)
            except Exception:
                logger.exception("The error after command: %s", name)

        return wrapper

    return log


def async_job_logger(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger.debug("Run %s", func.__name__)
        return await func(*args, **kwargs)

    return wrapper
