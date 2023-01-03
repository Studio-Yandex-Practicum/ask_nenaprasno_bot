from json import JSONDecodeError

import httpx
import uvicorn
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.authentication import requires
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from telegram import Bot
from telegram.error import TelegramError

from api import context_models
from bot.api import telegram_routes
from bot.bot import init_polling_api, init_webhook
from bot.service.bot_service import BotNotifierService
from core.config import settings
from core.logger import LOGGING_CONFIG, logger
from middleware import TokenAuthBackend
from service.api_client import APIService


async def start_bot() -> None:
    if settings.run_webhook:
        bot_app = await init_webhook()
        await bot_app.initialize()
        await bot_app.start()
    else:
        bot_app = await init_polling_api()

    api.state.bot_app = bot_app

    api.state.bot_service = BotNotifierService(bot_app)


async def stop_bot() -> None:
    await api.state.bot_app.stop()
    if not settings.run_webhook:
        await api.state.bot_app.updater.stop()
    await api.state.bot_app.shutdown()


async def healthcheck_api(request: Request) -> JSONResponse:
    health = context_models.HealthCheckResponseContext()
    bot: Bot = api.state.bot_app.bot
    try:
        await bot.get_me()
        health.bot_is_avaliable = True
    except TelegramError as error:
        logger.error("Failed to connect to bot: %s", error)

    try:
        api_service = APIService()
        bill = await api_service.get_bill()
        if bill is not None:
            health.site_api_is_avaliable = True
    except httpx.RequestError as error:
        logger.error("Failed to connect to database: %s", error)
    return JSONResponse(content=health.__dict__)


async def request_to_context(request: Request, context):
    body = await request.body()
    log_template = "%s %s %s\nRequest: %s"

    try:
        request_data: context = context.parse_obj(await request.json())
        logger.debug(log_template, request.method, request.url, httpx.codes.OK, body)
        return request_data
    except ValidationError as error:
        logger.error(log_template, request.method, request.url, httpx.codes.BAD_REQUEST, error)
        raise HTTPException(httpx.codes.BAD_REQUEST, f"ValidationError: {error}") from error
    except JSONDecodeError as error:
        logger.error(log_template, request.method, request.url, httpx.codes.BAD_REQUEST, body)
        raise HTTPException(httpx.codes.BAD_REQUEST, f"JSONDecodeError: {error}") from error


@requires("authenticated", status_code=401)
async def consultation_assign(request: Request) -> Response:
    request_data = await request_to_context(request, context_models.AssignedConsultationContext)
    if not request_data:
        return Response(status_code=httpx.codes.BAD_REQUEST)

    telegram_id = int(request_data.telegram_id)

    service = APIService()
    consultations_count = await service.get_consultations_count(telegram_id)
    await api.state.bot_service.consultation_assignment(request_data, consultations_count)
    return Response(status_code=httpx.codes.OK)


@requires("authenticated", status_code=401)
async def consultation_close(request: Request) -> Response:
    request_data = await request_to_context(request, context_models.ClosedConsultationContext)

    api.state.bot_service.consultation_close(request_data)
    return Response(status_code=httpx.codes.OK)


@requires("authenticated", status_code=401)
async def consultation_message(request: Request) -> Response:
    request_data = await request_to_context(request, context_models.ConsultationContext)
    if not request_data:
        return Response(status_code=httpx.codes.BAD_REQUEST)

    await api.state.bot_service.consultation_message(request_data)
    return Response(status_code=httpx.codes.OK)


@requires("authenticated", status_code=401)
async def consultation_feedback(request: Request) -> Response:
    request_data = await request_to_context(request, context_models.FeedbackConsultationContext)
    if not request_data:
        return Response(status_code=httpx.codes.BAD_REQUEST)

    await api.state.bot_service.consultation_feedback(request_data)
    return Response(status_code=httpx.codes.OK)


async def http_exception(request: Request, exc: HTTPException):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers)


exception_handlers = {HTTPException: http_exception}


def get_routes() -> list[Route]:
    routes = [
        Route("/healthcheck", healthcheck_api, methods=["GET"]),
        Route("/bot/consultation/assign", consultation_assign, methods=["POST"]),
        Route("/bot/consultation/close", consultation_close, methods=["POST"]),
        Route("/bot/consultation/message", consultation_message, methods=["POST"]),
        Route("/bot/consultation/feedback", consultation_feedback, methods=["POST"]),
    ]
    if settings.run_webhook:
        routes.extend(telegram_routes)
    return routes


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
