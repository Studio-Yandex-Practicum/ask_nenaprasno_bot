# pylint: disable=W0612
from json import JSONDecodeError

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.authentication import requires
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from telegram import Bot, Update
from telegram.error import TelegramError

from bot import DAILY_CONSULTATIONS_REMINDER_JOB, init_webhook
from core import config
from core.config import TRELLO_BORD_ID, URL_SITE
from core.logger import logger
from core.send_message import send_message
from middleware import TokenAuthBackend
from service.api_client import APIService
from service.models import (  # FeedbackConsultationModel,
    AssignedConsultationModel,
    ClosedConsultationModel,
    ConsultationModel,
    HealthCheckResponseModel,
)


async def start_bot() -> None:
    bot_app = await init_webhook()
    await bot_app.initialize()
    await bot_app.start()
    overdue_reminder = bot_app.job_queue.get_jobs_by_name(DAILY_CONSULTATIONS_REMINDER_JOB)[0]
    await overdue_reminder.run(bot_app)

    # provide bot started bot application to server via global state variable
    # https://www.starlette.io/applications/#storing-state-on-the-app-instance
    api.state.bot_app = bot_app


async def stop_bot() -> None:
    await api.state.bot_app.stop()
    await api.state.bot_app.shutdown()


async def healthcheck_api(request: Request) -> JSONResponse:
    health = HealthCheckResponseModel()
    bot: Bot = api.state.bot_app.bot
    try:
        await bot.get_me()
        health.bot_is_avaliable = True
    except TelegramError as error:
        logger.error("Failed to connect to bot: %s", error)

    try:
        api_service = APIService()
        bill = await api_service.get_bill()
        if bill is not None:
            health.site_api_is_avaliable = True
    except httpx.RequestError as error:
        logger.error("Failed to connect to database: %s", error)
    return JSONResponse(content=health.__dict__)


async def telegram_webhook_api(request: Request) -> Response:
    response = {}

    try:
        request_json = await request.json()
        bot_app = request.app.state.bot_app
        await bot_app.update_queue.put(Update.de_json(data=request_json, bot=bot_app.bot))
    except JSONDecodeError as error:
        logger.error("Got a JSONDecodeError: %s", error)
        response = {"status_code": httpx.codes.BAD_REQUEST}

    return Response(**response)


async def deserialize(request: Request, deserializer):
    try:
        request_data: deserializer = deserializer.from_dict(await request.json())
        logger.info("Got new api request: %s", request_data)
        return Response(status_code=httpx.codes.OK), request_data
    except KeyError as error:
        logger.error("Got a KeyError: %s", error)
        return Response(status_code=httpx.codes.BAD_REQUEST), None
    except JSONDecodeError as error:
        logger.error("Got a JSONDecodeError: %s", error)
        return Response(status_code=httpx.codes.BAD_REQUEST), None


@requires("authenticated", status_code=401)
async def consultation_assign(request: Request) -> Response:
    response, request_data = await deserialize(request, AssignedConsultationModel)
    if request_data is not None:
        bot = api.state.bot_app.bot
        chat_id = request_data.telegram_id
        text = (
            # ! uncomment when the consultation number is added to the API response and delete line after
            # f"Получена новая заявка №{request_data.consultation_number}\n"
            f"Получена новая заявка №<<TBA>>\n"
            f"[Открыть заявку на сайте]({URL_SITE}doctor/consultation/{request_data.consultation_id})\n"
            f"[Открыть Trello](https://trello.com/{TRELLO_BORD_ID}/?filter=member:{request_data.username_trello})\n\n"
        )
        await send_message(bot=bot, chat_id=chat_id, text=text)
    return response


@requires("authenticated", status_code=401)
async def consultation_close(request: Request) -> Response:
    # ! add second variable similar to consultation_assign once the site API response is fixed
    response, _ = await deserialize(request, ClosedConsultationModel)
    # ! request a sample text for the close message
    # if request_data is not None:
    #     bot = api.state.bot_app.bot
    #     chat_id = request_data.telegram_id
    #     text = (f"Заявка №{request_data.consultation_number} закрыта\n")
    #     await send_message(bot=bot, chat_id=chat_id, text=text)
    return response


@requires("authenticated", status_code=401)
async def consultation_message(request: Request) -> Response:
    response, request_data = await deserialize(request, ConsultationModel)
    if request_data is not None:
        bot = api.state.bot_app.bot
        chat_id = request_data.telegram_id
        text = (
            # ! uncomment when the consultation number is added to the API response and delete line after
            # f"Получено новое сообщение в чате заявки №{request_data.consultation_number}\n"
            f"Получено новое сообщение в чате заявки №<<TBA>>\n"
            f"[Открыть заявку на сайте]({URL_SITE}doctor/consultation/{request_data.consultation_id})\n"
            f"[Открыть Trello](https://trello.com/{TRELLO_BORD_ID}/?filter=member:{request_data.username_trello})\n\n"
        )
        await send_message(bot=bot, chat_id=chat_id, text=text)
    return response


@requires("authenticated", status_code=401)
async def consultation_feedback(request: Request) -> Response:
    # ! site API does not return the message from the feedback, right now ConsultationModel
    # ! information is provided, without the consultation_response. Once fixed,
    # ! uncomment next line, delete line after
    # response, request_data = await deserialize(request, FeedbackConsultationModel)
    response, request_data = await deserialize(request, ConsultationModel)
    if request_data is not None:
        bot = api.state.bot_app.bot
        chat_id = request_data.telegram_id
        text = (
            # ! uncomment next line when the consultation number is added to the API response and delete line after
            # f"Вы получили новый отзыв по заявке №{request_data.consultation_number}\n"
            f"Вы получили новый отзыв по заявке №<<TBA>>\n"
            # ! uncomment next line when the consultation response is added to the API response
            # f"{request_data.consultation_response})\n"
            f"[Открыть Trello](https://trello.com/{TRELLO_BORD_ID}"
            f"/?filter=member:{request_data.username_trello},dueComplete:true)\n\n"
        )
        await send_message(bot=bot, chat_id=chat_id, text=text)

    return response


routes = [
    Route("/telegramWebhookApi", telegram_webhook_api, methods=["POST"]),
    Route("/healthcheck", healthcheck_api, methods=["GET"]),
    Route("/bot/consultation/assign", consultation_assign, methods=["POST"]),
    Route("/bot/consultation/close", consultation_close, methods=["POST"]),
    Route("/bot/consultation/message", consultation_message, methods=["POST"]),
    Route("/bot/consultation/feedback", consultation_feedback, methods=["POST"]),
]

middleware = [Middleware(AuthenticationMiddleware, backend=TokenAuthBackend())]

api = Starlette(routes=routes, on_startup=[start_bot], on_shutdown=[stop_bot], middleware=middleware)


if __name__ == "__main__":
    uvicorn.run(app=api, debug=True, host=config.HOST, port=config.PORT)
