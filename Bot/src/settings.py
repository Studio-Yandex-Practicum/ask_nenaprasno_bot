from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from telegram import Update


async def health(request: Request) -> PlainTextResponse:
    bot_app = request.app.state.bot
    return PlainTextResponse(content="Бот все еще запущен :)")


async def telegram(request: Request) -> Response:
    bot_app = request.app.state.bot
    await bot_app.update_queue.put(Update.de_json(data=await request.json(), bot=bot_app.bot))
    return Response()


routes = [
    Route("/telegram", telegram, methods=["POST"]),
    Route("/health", health, methods=["GET"]),
]
