import uvicorn

from telegram import Update
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route

from bot import init_webhook, init_pooling
import config


async def main():
    app = await init_webhook()

    async def telegram(request: Request) -> Response:
        await app.update_queue.put(
            Update.de_json(data=await request.json(), bot=app.bot)
        )
        return Response()

    async def health(_: Request) -> PlainTextResponse:
        return PlainTextResponse(content="The bot is still running fine :)")

    starlette_app = Starlette(
        routes=[
            Route("/telegram", telegram, methods=["POST"]),
            Route("/health", health, methods=["GET"]),
        ]
    )

    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=starlette_app,
            port=config.PORT,
            use_colors=False,
            host=config.HOST,
        )
    )

    async with app:
        await app.start()
        await webserver.serve()
        await app.stop()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
