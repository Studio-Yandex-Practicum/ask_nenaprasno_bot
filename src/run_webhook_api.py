from dotenv import load_dotenv
from json import JSONDecodeError

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from telegram import Bot, Update
from telegram.error import TelegramError

from bot import init_webhook
from core import config
from core.logger import logger
from service.api_client import APIService
from service.constants import ACTION_TO_DESERIALIZER
from service.models import HealthCheckResponseModel
from utils import check_token


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


async def nenaprasno_dispatcher(request: Request) -> Response:

    is_authorized = await check_token(request)
    if not is_authorized:
        return Response(status_code=httpx.codes.UNAUTHORIZED)

    try:
        deserializer = ACTION_TO_DESERIALIZER[request.path_params["action"]]
    except KeyError as error:
        logger.error(f"Got a wrong action: {error}")
        return Response(status_code=httpx.codes.BAD_REQUEST)

    try:
        request_data: deserializer = deserializer.from_dict(await request.json())
        logger.info(f"Got new api request: {request_data}")
        return Response(status_code=httpx.codes.OK)
    except KeyError as error:
        logger.error(f"Got a KeyError: {error}")
        return Response(status_code=httpx.codes.BAD_REQUEST)
    except JSONDecodeError as error:
        logger.error(f"Got a JSONDecodeError: {error}")
        return Response(status_code=httpx.codes.BAD_REQUEST)

routes = [
    Route("/telegramWebhookApi", telegram_webhook_api, methods=["POST"]),
    Route("/healthcheck", healthcheck_api, methods=["GET"]),
    Route("/bot/consultation/{action:str}", nenaprasno_dispatcher, methods=["POST"])
]

api = Starlette(routes=routes, on_startup=[start_bot], on_shutdown=[stop_bot])


if __name__ == "__main__":
    uvicorn.run(app=api, debug=True, host=config.HOST, port=config.PORT)
