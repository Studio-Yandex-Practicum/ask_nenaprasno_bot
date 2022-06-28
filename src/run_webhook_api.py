import httpx
import json
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from telegram import Update

from core import config
from bot import init_webhook
from core.logger import logging


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


async def healthcheck_api(request: Request) -> PlainTextResponse:
    message: str = f"Бот запущен и работает. Сообщение получено по запросу на Api сервера {config.WEBHOOK_URL}"

    logging.info(message)

    return PlainTextResponse(content=f'Request has been received and logged: "{message}"')


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
    response_json: dict = dict(await request.json())
    try:
        trello_model_id: int = response_json["model"]["id"]
        logging.info(f"Got trello request, model id: {trello_model_id}.")
    except KeyError:
        logging.info("Got not trello or empty request.")
    except json.decoder.JSONDecodeError:
        logging.info("Got data is not json.")
    finally:
        return Response("Message received.", status_code=httpx.codes.OK)


routes = [
    Route("/telegramWebhookApi", telegram_webhook_api, methods=["POST"]),
    Route("/healthcheck", healthcheck_api, methods=["GET"]),
    Route("/trelloWebhookApi", trello_webhook_api, methods=["POST", "HEAD"]),
]

api = Starlette(routes=routes, on_startup=[start_bot], on_shutdown=[stop_bot])

if __name__ == '__main__':
    uvicorn.run(app=api, debug=True, host=config.HOST, port=config.PORT)
