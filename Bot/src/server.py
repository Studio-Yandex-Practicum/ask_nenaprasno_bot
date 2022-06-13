from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from telegram import Update


async def health(_: Request) -> PlainTextResponse:
    return PlainTextResponse(content="Бот все еще запущен :)")


async def telegram(request: Request) -> Response:
    await request.app.update_queue.put(Update.de_json(data=await request.json(), bot=request.app.bot))
    return Response()


routes = [
    Route("/telegram", telegram, methods=["POST"]),
    Route("/health", health, methods=["GET"]),
]
