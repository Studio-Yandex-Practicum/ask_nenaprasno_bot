# pylint: disable=W1203
from core.config import DEBUG
from core.logger import debug_logger


def async_log_api_requests(func):
    async def wrapper(*args, **kwargs):
        if DEBUG is True:
            url = kwargs.get("url")
            if url is not None:
                debug_logger.debug(f"Request to {url}")

        return await func(*args, **kwargs)

    return wrapper
