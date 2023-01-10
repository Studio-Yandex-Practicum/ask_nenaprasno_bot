from json import JSONDecodeError

import httpx
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from telegram import Update

from core.logger import logger


async def telegram_webhook_api(request: Request) -> Response:
    response = {}

    try:
        request_json = await request.json()
        bot_app = request.app.state.bot_app
        await bot_app.update_queue.put(Update.de_json(data=request_json, bot=bot_app.bot))
    except JSONDecodeError as error:
        logger.error("Got a JSONDecodeError: %s", error)
        response = {"status_code": httpx.codes.BAD_REQUEST}

    return Response(**response)


telegram_routes = [
    Route("/telegramWebhookApi", telegram_webhook_api, methods=["POST"]),
]
