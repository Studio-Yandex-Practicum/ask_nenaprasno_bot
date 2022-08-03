from core.exceptions import EnvVariablesError


def safe_conversion(func):
    def wrapper(*args):
        try:
            return func(*args)
        except Exception as exc:
            raise EnvVariablesError(*args) from exc

    return wrapper
