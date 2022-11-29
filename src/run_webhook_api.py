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
from telegram import Bot, Update
from telegram.error import TelegramError

from api import context_models
from bot import init_webhook
from core.config import settings
from core.exceptions import BadRequestError
from core.logger import LOGGING_CONFIG, logger
from middleware import TokenAuthBackend
from service.api_client import APIService
from service.bot_service import BotNotifierService
from service.models import (
    AssignedConsultationModel,
    ConsultationModel,
    FeedbackConsultationModel,
    HealthCheckResponseModel,
)


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


async def healthcheck_api(request: Request) -> JSONResponse:
    health = HealthCheckResponseModel()
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


async def deserialize(request: Request, deserializer):
    body = await request.body()
    log_template = "%s %s %s\nRequest: %s"

    try:
        request_data: deserializer = deserializer.from_dict(await request.json())
        logger.debug(log_template, request.method, request.url, httpx.codes.OK, body)
        return request_data
    except KeyError as error:
        logger.error(log_template, request.method, request.url, httpx.codes.BAD_REQUEST, body)
        raise BadRequestError(f"KeyError: {error} key not found") from error
    except JSONDecodeError as error:
        logger.error(log_template, request.method, request.url, httpx.codes.BAD_REQUEST, body)
        raise BadRequestError(f"JSONDecodeError: {error}") from error


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
    try:
        request_data = await deserialize(request, AssignedConsultationModel)
    except BadRequestError as error:
        logger.error("%s", error)
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
    request_data = await deserialize(request, ConsultationModel)
    if not request_data:
        return Response(status_code=httpx.codes.BAD_REQUEST)

    await api.state.bot_service.consultation_message(request_data)
    return Response(status_code=httpx.codes.OK)


@requires("authenticated", status_code=401)
async def consultation_feedback(request: Request) -> Response:
    request_data = await deserialize(request, FeedbackConsultationModel)
    if not request_data:
        return Response(status_code=httpx.codes.BAD_REQUEST)

    await api.state.bot_service.consultation_feedback(request_data)
    return Response(status_code=httpx.codes.OK)


async def http_exception(request: Request, exc: HTTPException):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers)


exception_handlers = {HTTPException: http_exception}


routes = [
    Route("/telegramWebhookApi", telegram_webhook_api, methods=["POST"]),
    Route("/healthcheck", healthcheck_api, methods=["GET"]),
    Route("/bot/consultation/assign", consultation_assign, methods=["POST"]),
    Route("/bot/consultation/close", consultation_close, methods=["POST"]),
    Route("/bot/consultation/message", consultation_message, methods=["POST"]),
    Route("/bot/consultation/feedback", consultation_feedback, methods=["POST"]),
]

middleware = [Middleware(AuthenticationMiddleware, backend=TokenAuthBackend())]

api = Starlette(
    routes=routes,
    on_startup=[start_bot],
    on_shutdown=[stop_bot],
    middleware=middleware,
    exception_handlers=exception_handlers,
)


if __name__ == "__main__":
    uvicorn.run(app=api, debug=True, host=settings.host, port=settings.port, log_config=LOGGING_CONFIG)
