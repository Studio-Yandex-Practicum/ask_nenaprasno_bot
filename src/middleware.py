from typing import Optional, Tuple

from starlette.authentication import (AuthCredentials,
                                      AuthenticationBackend,
                                      SimpleUser)
from starlette.requests import HTTPConnection

from core import config
from core.logger import logger


class TokenAuthBackend(AuthenticationBackend):

    CREDENTIALS = {
        'Authorization': {
            'username': 'nenaprasno',
            'token': config.BOT_API_SITE_TOKEN,
        },
        'X-Telegram-Bot-Api-Secret-Token': {
            'username': 'telegram',
            'token': config.SECRET_TELEGRAM_TOKEN,
        },
    }

    async def authenticate(
        self, conn: HTTPConnection
    ) -> Optional[Tuple[AuthCredentials, SimpleUser]]:

        for header in self.CREDENTIALS.keys():
            if header in conn.headers:
                request_token = conn.headers[header]
                actual_token = self.CREDENTIALS[header]['token']
                user = self.CREDENTIALS[header]['username']
                if request_token == actual_token:
                    logger.info(f'Got a request from {user}')
                    return AuthCredentials(['authenticated']), SimpleUser(user)
                else:
                    logger.warning(f'Unauthorized access attempt with token {request_token}')
                    return None
        logger.warning('Unauthorized access attempt without token')
        return None
