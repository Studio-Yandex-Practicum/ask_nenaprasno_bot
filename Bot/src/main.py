import uvicorn

from contextlib import asynccontextmanager
from starlette.applications import Starlette
from typing import AsyncGenerator

from bot import init
from core import config
from server import routes


@asynccontextmanager
async def manage_bot(app: Starlette) -> AsyncGenerator:
    """
    Create bot managing generator
    :param app: Starlette application
    :return: Async generator
    """
    async with init() as bot:
        app.state.bot = bot
        yield


app = Starlette(routes=routes, lifespan=manage_bot)


if __name__ == '__main__':
    uvicorn.run(app=app, debug=True, host=config.HOST, port=config.PORT)
