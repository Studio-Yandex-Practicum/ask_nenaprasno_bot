from core.logger import logger


class EnvVariablesError(Exception):
    """Exception class for errors caused by type conversion of environment variables."""

    def __init__(self, setting, setting_value, message="The value is not converted to the expected type."):
        self.setting = setting
        self.setting_value = setting_value
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        err = f"{self.setting}={self.setting_value} -> {self.message}"
        logger.error(("The error: '%s'", str(err)))
        return err
