import uvicorn

from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from telegram import Update

from bot import init
from core import config


async def run_server():
    bot_app = init(webhook=True)

    async def run_bot() -> None:
        await bot_app.bot.set_webhook(url=f"{config.WEBHOOK_URL}/telegram")

    @asynccontextmanager
    async def manage_bot(app):
        async with run_bot():
            yield

    async def telegram(request: Request) -> Response:
        await bot_app.update_queue.put(
            Update.de_json(data=await request.json(), bot=bot_app.bot)
        )
        return Response()

    async def health(_: Request) -> PlainTextResponse:
        return PlainTextResponse(content="Бот все еще запущен :)")

    routes = [
        Route("/telegram", telegram, methods=["POST"]),
        Route("/health", health, methods=["GET"]),
    ]

    return Starlette(routes=routes, lifespan=manage_bot)
