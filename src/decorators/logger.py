def async_error_logger(name, logger):
    """Logs errors in wrapped asyc functions."""
    def log(func):
        async def wrapper(*args, **kwargs):
            try:
                await func(*args, **kwargs)
            except Exception as err:
                logger.error(f"The error: '{str(err)}' after command: "
                             f"'{name}'")
        return wrapper
    return log


def sync_error_logger(name, logger):
    """Logs errors in wrapped sync functions."""
    def log(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as err:
                logger.error(f"The error: '{str(err)}' after command: "
                             f"'{name}'")
        return wrapper
    return log
