import uvicorn
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from api.routes import routes, telegram_routes
from bot.bot import init_polling_api, init_webhook
from bot.service.bot_service import BotNotifierService
from core.config import settings
from core.logger import LOGGING_CONFIG, logger
from middleware import TokenAuthBackend


async def start_bot() -> None:
    if settings.run_webhook:
        bot_app = await init_webhook()
    else:
        bot_app = await init_polling_api()

    api.state.bot_app = bot_app

    api.state.bot_service = BotNotifierService(bot_app)


async def stop_bot() -> None:
    await api.state.bot_app.stop()
    if not settings.run_webhook:
        await api.state.bot_app.updater.stop()
    await api.state.bot_app.shutdown()
    logger.debug("The bot has been stopped")


async def http_exception(request: Request, exc: HTTPException):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers)


def get_routes() -> list[Route]:
    if settings.run_webhook:
        routes.extend(telegram_routes)
    return routes


exception_handlers = {HTTPException: http_exception}
middleware = [Middleware(AuthenticationMiddleware, backend=TokenAuthBackend())]
api = Starlette(
    routes=get_routes(),
    on_startup=[start_bot],
    on_shutdown=[stop_bot],
    middleware=middleware,
    exception_handlers=exception_handlers,
)


if __name__ == "__main__":
    uvicorn.run(app=api, debug=True, host=settings.host, port=settings.port, log_config=LOGGING_CONFIG)
