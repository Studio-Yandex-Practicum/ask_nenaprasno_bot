from json import JSONDecodeError

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from telegram import Update

from src.api.routes import routes
from src.bot import init_webhook
from src.core.config import settings
from src.core.logger import LOGGING_CONFIG, logger
from src.middleware import TokenAuthBackend
from src.service.bot_service import BotNotifierService


async def start_bot() -> None:
    bot_app = await init_webhook()
    await bot_app.initialize()
    await bot_app.start()

    # provide bot started bot application to server via global state variable
    # https://www.starlette.io/applications/#storing-state-on-the-app-instance

    # Удалить пермененную после переноса всех методов в класс BotNotifierService
    api.state.bot_app = bot_app

    api.state.bot_service = BotNotifierService(bot_app)


async def stop_bot() -> None:
    await api.state.bot_app.stop()
    await api.state.bot_app.shutdown()


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


async def http_exception(request: Request, exc: HTTPException):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers)


exception_handlers = {HTTPException: http_exception}

middleware = [Middleware(AuthenticationMiddleware, backend=TokenAuthBackend())]


telegram_routes = [
    Route("/telegramWebhookApi", telegram_webhook_api, methods=["POST"]),
]

all_routes = telegram_routes + routes


api = Starlette(
    routes=all_routes,
    on_startup=[start_bot],
    on_shutdown=[stop_bot],
    middleware=middleware,
    exception_handlers=exception_handlers,
)

if __name__ == "__main__":
    uvicorn.run(app=api, debug=True, host=settings.host, port=settings.port, log_config=LOGGING_CONFIG)
