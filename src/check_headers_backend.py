import os
from typing import Optional, Tuple

from starlette.authentication import (AuthCredentials,
                                      AuthenticationBackend,
                                      SimpleUser)
from starlette.requests import HTTPConnection

from core.logger import logger


class CheckHeadersBackend(AuthenticationBackend):
    async def authenticate(
        self, conn: HTTPConnection
    ) -> tuple[AuthCredentials, SimpleUser] | AuthCredentials | None:

        if 'Authorization' in conn.headers:
            token = conn.headers['authorization']
            if token == os.getenv('SITE_API_BOT_TOKEN'):
                return AuthCredentials(['authenticated']), SimpleUser('nenaprasno')
            else:
                logger.warning(f'Unauthorized access attempt with token {token}')

        elif 'X-Telegram-Bot-Api-Secret-Token' in conn.headers:
            token = conn.headers['X-Telegram-Bot-Api-Secret-Token']
            if token == os.getenv('SECRET_TOKEN'):
                return AuthCredentials(['authenticated']), SimpleUser('telegram')
            else:
                logger.warning(f'Unauthorized access attempt with token {token}')

        else:
            logger.warning('Unauthorized access attempt without token')
        return
