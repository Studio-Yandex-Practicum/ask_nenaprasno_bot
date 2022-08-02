import httpx
import os
from typing import Union

from starlette.requests import Request
from starlette.responses import Response

from core.logger import logger


async def check_token(request: Request) -> Union[None, Response]:
    token = request.headers.get("authorization")
    if token != os.getenv("SITE_API_BOT_TOKEN"):
        logger.warning(
            f"Unauthorized access attempt {('with token ' + token) if token else 'without token'}"
        )
        return Response(status_code=httpx.codes.UNAUTHORIZED)
