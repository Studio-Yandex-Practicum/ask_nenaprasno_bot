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
from service.trello_data_deserializer import TrelloDeserializerModel
from service.healthcheck_serializer import HealthSerializerModel
from create_trello_webhook import trello_webhook


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
    health = HealthSerializerModel()
    bot: Bot = api.state.bot_app.bot
    try:
        await bot.get_me()
        health.bot_is_avaliable = True
    except TelegramError as error:
        logger.error(f"Failed to connect to bot: {error}")

    try:
        api_service = APIService()
        api_service.get_bill()
        health.db_is_avaliable = True
    except Exception as error:
        logger.error(f"Failed to connect to database: {error}")

    return JSONResponse(content=health.to_dict())


async def telegram_webhook_api(request: Request) -> Response:
    bot_app = request.app.state.bot_app
    await bot_app.update_queue.put(Update.de_json(data=await request.json(), bot=bot_app.bot))
    return Response()


async def trello_webhook_api(request: Request) -> Response:
    """
    Plug func catching trello post request
    :param request: Trello request
    :return: Response "ok"
    """
    try:
        trello_data: TrelloDeserializerModel = TrelloDeserializerModel.from_dict(await request.json())
        logger.info(f"Got new trello request: {trello_data}.")
        return Response(status_code=httpx.codes.OK)
    except KeyError as error:
        logger.error(f"Got a KeyError: {error}")
        return Response(status_code=httpx.codes.BAD_REQUEST)
    except JSONDecodeError as error:
        logger.error(f"Got a JSONDecodeError: {error}")
        return Response(status_code=httpx.codes.OK)


routes = [
    Route("/telegramWebhookApi", telegram_webhook_api, methods=["POST"]),
    Route("/healthcheck", healthcheck_api, methods=["GET"]),
    Route("/trelloWebhookApi", trello_webhook_api, methods=["POST", "HEAD"]),
]

api = Starlette(routes=routes, on_startup=[start_bot, trello_webhook], on_shutdown=[stop_bot])


if __name__ == "__main__":
    uvicorn.run(app=api, debug=True, host=config.HOST, port=config.PORT)
