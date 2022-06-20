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
