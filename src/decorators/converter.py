from functools import wraps

from core import get_string
from core.exceptions import EnvVariablesError
from core.logger import logger


def get_safe_env_variables_decorator(func):
    @wraps(func)
    def wrapper(setting):
        try:
            return func(setting)
        except Exception as exc:
            logger.exception(setting)
            raise EnvVariablesError(setting) from exc

    return wrapper


def get_env_value_string_representation_by_name(func):
    @wraps(func)
    def wrapper(setting):
        return func(get_string(setting))

    return wrapper
