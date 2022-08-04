from json import JSONDecodeError

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from telegram import Bot, Update
from telegram.error import TelegramError

from bot import init_webhook
from check_headers_backend import CheckHeadersBackend
from core import config
from core.logger import logger
from service.api_client import APIService
from service.bot_api_data_deserializers import (AssignDeserializerModel,
                                                CloseDeserializerModel,
                                                MessageFeedbackDeserializerModel)
from service.models import HealthCheckResponseModel


load_dotenv()


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
        logger.error(f"Failed to connect to bot: {error}")

    try:
        api_service = APIService()
        bill = await api_service.get_bill()
        if bill is not None:
            health.site_api_is_avaliable = True
    except Exception as error:
        logger.error(f"Failed to connect to database: {error}")

    return JSONResponse(content=health.to_dict())


async def telegram_webhook_api(request: Request) -> Response:
    bot_app = request.app.state.bot_app
    await bot_app.update_queue.put(Update.de_json(data=await request.json(), bot=bot_app.bot))
    return Response()


async def try_to_deserialize(request: Request, deserializer):
    try:
        request_data: deserializer = deserializer.from_dict(await request.json())
        logger.info(f"Got new api request: {request_data}")
        return Response(status_code=httpx.codes.OK), request_data
    except KeyError as error:
        logger.error(f"Got a KeyError: {error}")
        return Response(status_code=httpx.codes.BAD_REQUEST), None
    except JSONDecodeError as error:
        logger.error(f"Got a JSONDecodeError: {error}")
        return Response(status_code=httpx.codes.BAD_REQUEST), None


async def consultation_assign(request: Request) -> Response:
    deserializer = AssignDeserializerModel
    if request.user.is_authenticated:
        response, request_data = await try_to_deserialize(request, deserializer)
        return response
    return Response(status_code=httpx.codes.UNAUTHORIZED)


async def consultation_close(request: Request) -> Response:
    deserializer = CloseDeserializerModel
    if request.user.is_authenticated:
        response, request_data = await try_to_deserialize(request, deserializer)
        return response
    return Response(status_code=httpx.codes.UNAUTHORIZED)


async def consultation_message(request: Request) -> Response:
    deserializer = MessageFeedbackDeserializerModel
    if request.user.is_authenticated:
        response, request_data = await try_to_deserialize(request, deserializer)
        return response
    return Response(status_code=httpx.codes.UNAUTHORIZED)


async def consultation_feedback(request: Request) -> Response:
    deserializer = MessageFeedbackDeserializerModel
    if request.user.is_authenticated:
        response, request_data = await try_to_deserialize(request, deserializer)
        return response
    return Response(status_code=httpx.codes.UNAUTHORIZED)


routes = [
    Route("/telegramWebhookApi", telegram_webhook_api, methods=["POST"]),
    Route("/healthcheck", healthcheck_api, methods=["GET"]),
    Route("/bot/consultation/assign", consultation_assign, methods=["POST"]),
    Route("/bot/consultation/close", consultation_close, methods=["POST"]),
    Route("/bot/consultation/message", consultation_message, methods=["POST"]),
    Route("/bot/consultation/feedback", consultation_feedback, methods=["POST"]),
]

middleware = [
    Middleware(TrustedHostMiddleware, allowed_hosts=[os.getenv('SITE_API_URL'), os.getenv('WEBHOOK_URL')]),
    Middleware(AuthenticationMiddleware, backend=CheckHeadersBackend())
]

api = Starlette(routes=routes, on_startup=[start_bot], on_shutdown=[stop_bot], middleware=middleware)


if __name__ == "__main__":
    uvicorn.run(app=api, debug=True, host=config.HOST, port=config.PORT)
