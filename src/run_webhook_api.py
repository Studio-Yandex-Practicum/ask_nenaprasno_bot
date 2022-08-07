from json import JSONDecodeError

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.authentication import requires
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from telegram import Bot, Update
from telegram.error import TelegramError

from bot import init_webhook
from core import config
from core.logger import logger
from core.send_message import send_new_message_notification
from middleware import TokenAuthBackend
from service.api_client import APIService
from service.models import (
    AssignedConsultationModel,
    ClosedConsultationModel,
    ConsultationModel,
    HealthCheckResponseModel,
)


async def start_bot() -> None:
    bot_app = await init_webhook()
    await bot_app.initialize()
    await bot_app.start()

    # provide bot started bot application to server via global state variable
    # https://www.starlette.io/applications/#storing-state-on-the-app-instance
    api.state.bot_app = bot_app


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
    bot_app = request.app.state.bot_app
    await bot_app.update_queue.put(Update.de_json(data=await request.json(), bot=bot_app.bot))
    return Response()


async def deserialize(request: Request, deserializer):
    try:
        request_data: deserializer = deserializer.from_dict(await request.json())
        logger.info("Got new api request: %s", request_data)
        return Response(status_code=httpx.codes.OK), request_data
    except KeyError as error:
        logger.error("Got a KeyError: %s", error)
        return Response(status_code=httpx.codes.BAD_REQUEST), None
    except JSONDecodeError as error:
        logger.error("Got a JSONDecodeError: %s", error)
        return Response(status_code=httpx.codes.BAD_REQUEST), None


@requires("authenticated", status_code=401)
async def consultation_assign(request: Request) -> Response:
    response, _ = await deserialize(request, AssignedConsultationModel)
    # add second variable as in consultation_message when will work with it
    return response


@requires("authenticated", status_code=401)
async def consultation_close(request: Request) -> Response:
    response, _ = await deserialize(request, ClosedConsultationModel)
    # add second variable as in consultation_message when will work with it
    return response


@requires("authenticated", status_code=401)
async def consultation_message(request: Request) -> Response:
    response, request_data = await deserialize(request, ConsultationModel)
    bot: Bot = api.state.bot_app.bot
    await send_new_message_notification(bot, request_data)
    return response


@requires("authenticated", status_code=401)
async def consultation_feedback(request: Request) -> Response:
    response, _ = await deserialize(request, ConsultationModel)
    # add second variable as in consultation_message when will work with it
    return response


routes = [
    Route("/telegramWebhookApi", telegram_webhook_api, methods=["POST"]),
    Route("/healthcheck", healthcheck_api, methods=["GET"]),
    Route("/bot/consultation/assign", consultation_assign, methods=["POST"]),
    Route("/bot/consultation/close", consultation_close, methods=["POST"]),
    Route("/bot/consultation/message", consultation_message, methods=["POST"]),
    Route("/bot/consultation/feedback", consultation_feedback, methods=["POST"]),
]

middleware = [Middleware(AuthenticationMiddleware, backend=TokenAuthBackend())]

api = Starlette(routes=routes, on_startup=[start_bot], on_shutdown=[stop_bot], middleware=middleware)


if __name__ == "__main__":
    uvicorn.run(app=api, debug=True, host=config.HOST, port=config.PORT)
