import uvicorn

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackContext

import config


async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я постараюсь помочь вам.")


def add_handlers(app: Application) -> None:
    """
    Add handlers to telegram bot application
    :param app: Telegram bot application
    """
    handlers = {
        CommandHandler: (
            ("start", start),
        ),
    }
    for handler in handlers:
        for params in handlers[handler]:
            app.add_handler(handler(*params))


async def init_webhook() -> None:
    app = Application.builder().updater(None).token(config.TOKEN).build()

    add_handlers(app)

    await app.bot.set_webhook(url=f"{config.WEBHOOK_URL}/telegram")

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


def init_pooling():
    app = ApplicationBuilder().token(config.TOKEN).build()

    add_handlers(app)

    app.run_polling()
    return app
