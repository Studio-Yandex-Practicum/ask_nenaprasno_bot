from functools import wraps

from core import get_string
from core.exceptions import EnvVariablesError


def get_safe_env_variables_decorator(func):
    @wraps(func)
    def wrapper(setting):
        setting_value = get_string(setting)
        try:
            return func(setting_value)
        except Exception as exc:
            raise EnvVariablesError(setting, setting_value) from exc

    return wrapper


def get_env_value_string_representation_by_name(func):
    @wraps(func)
    def wrapper(setting):
        return func(get_string(setting))

    return wrapper
