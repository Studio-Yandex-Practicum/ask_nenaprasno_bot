import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from telegram import Update

from bot import init_webhook
from core import config


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


async def health(request: Request) -> PlainTextResponse:
    message = f"Бот запущен и работает. Сообщение получено по запросу на Api сервера {config.WEBHOOK_URL}"
    chat_id = config.CHAT_ID
    await request.app.state.bot_app.bot.send_message(
        chat_id=chat_id, text=message
    )

    return PlainTextResponse(content=f"Message send to bot: {message}")


async def telegram(request: Request) -> Response:
    bot_app = request.app.state.bot_app
    await bot_app.update_queue.put(Update.de_json(data=await request.json(), bot=bot_app.bot))
    return Response()


routes = [
    Route("/telegram", telegram, methods=["POST"]),
    Route("/health", health, methods=["GET"]),
]

api = Starlette(routes=routes, on_startup=[start_bot], on_shutdown=[stop_bot])

if __name__ == '__main__':
    uvicorn.run(app=api, debug=True, host=config.HOST, port=config.PORT)
