import uvicorn

from starlette.applications import Starlette

from bot import manage_bot
from core import config
from settings import routes


STARLETTE_API = Starlette(routes=routes, lifespan=manage_bot)


if __name__ == '__main__':
    uvicorn.run(app=STARLETTE_API, debug=True, host=config.HOST, port=config.PORT)
