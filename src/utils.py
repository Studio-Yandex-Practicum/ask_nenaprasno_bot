import os

from starlette.requests import Request

from core.logger import logger


async def check_token(request: Request) -> bool:
    token = request.headers.get("authorization")
    if token == os.getenv("SITE_API_BOT_TOKEN"):
        return True
    logger.warning(
        f"Unauthorized access attempt {('with token ' + token) if token else 'without token'}"
    )
    return False
