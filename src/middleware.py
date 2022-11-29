from typing import Optional, Tuple

from starlette.authentication import AuthCredentials, AuthenticationBackend, SimpleUser
from starlette.requests import HTTPConnection

from core.config import settings
from core.logger import logger


class TokenAuthBackend(AuthenticationBackend):
    CREDENTIALS = {
        "Authorization": {
            "username": "nenaprasno",
            "token": settings.site_api_bot_token,
        },
        "X-Telegram-Bot-Api-Secret-Token": {
            "username": "telegram",
            "token": settings.secret_telegram_token,
        },
    }

    def get_auth_credentials(
        self, request_token: str, header_value: dict
    ) -> Optional[Tuple[AuthCredentials, SimpleUser]]:
        actual_token = header_value["token"]
        user = header_value["username"]

        if request_token == actual_token:
            logger.info("Got a request from %s", user)
            return AuthCredentials(["authenticated"]), SimpleUser(user)

        logger.warning("Unauthorized access attempt with token %s", request_token)
        return None

    async def authenticate(self, conn: HTTPConnection) -> Optional[Tuple[AuthCredentials, SimpleUser]]:
        for header, header_value in self.CREDENTIALS.items():
            if header in conn.headers:
                request_token = conn.headers[header]
                return self.get_auth_credentials(request_token, header_value)

        logger.warning("Unauthorized access attempt without token")
        return None
