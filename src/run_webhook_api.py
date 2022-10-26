# pylint: disable=W0612
from json import JSONDecodeError
from typing import Tuple

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

from bot import init_webhook
from core import config
from core.logger import logger
from core.send_message import send_message
from core.utils import build_consultation_url, build_trello_url, get_word_case, get_word_genitive
from middleware import TokenAuthBackend
from service.api_client import APIService
from service.models import (
    AssignedConsultationModel,
    ClosedConsultationModel,
    ConsultationModel,
    FeedbackConsultationModel,
    HealthCheckResponseModel,
)
from texts.bot import API_CONSULTATION_MESSAGE, API_NEW_CONSULTATION, API_NEW_FEEDBACK
from texts.common import PLURAL_CONSULTATION, PLURAL_CONSULTATION_NOT_SINGLE


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
        return request_data
    except (KeyError, JSONDecodeError) as error:
        logger.error("Got exception %s while processing API request: %s", type(error).__name__, error)
        return None


@requires("authenticated", status_code=401)
async def consultation_assign(request: Request) -> Response:
    consultation = await deserialize(request, AssignedConsultationModel)
    if not consultation:
        return Response(status_code=httpx.codes.BAD_REQUEST)

    telegram_id = int(consultation.telegram_id)

    service = APIService()
    active_cons_count, expired_cons_count = await service.get_consultations_count(telegram_id)
    declination_consultation = get_word_case(active_cons_count, *PLURAL_CONSULTATION)
    genitive_declination_consultation = get_word_genitive(expired_cons_count, *PLURAL_CONSULTATION_NOT_SINGLE)

    site_url = build_consultation_url(consultation.consultation_id)
    trello_url = build_trello_url(consultation.username_trello)

    text = API_NEW_CONSULTATION.format(
        consultation_number=consultation.consultation_number,
        site_url=site_url,
        active_cons_count=active_cons_count,
        declination_consultation=declination_consultation,
        expired_cons_count=expired_cons_count,
        genitive_declination_consultation=genitive_declination_consultation,
        trello_url=trello_url,
    )
    await send_message(api.state.bot_app.bot, telegram_id, text)
    return Response(status_code=httpx.codes.OK)


@requires("authenticated", status_code=401)
async def consultation_close(request: Request) -> Response:
    request_data = await deserialize(request, ClosedConsultationModel)
    if not request_data:
        return Response(status_code=httpx.codes.BAD_REQUEST)

    consultation_id = request_data.consultation_id
    bot_app = api.state.bot_app
    reminder_jobs = bot_app.job_queue.jobs()
    for job in reminder_jobs:
        if isinstance(job.data, Tuple) and job.data[0] == consultation_id:
            job.schedule_removal()
    return Response(status_code=httpx.codes.OK)


@requires("authenticated", status_code=401)
async def consultation_message(request: Request) -> Response:
    consultation = await deserialize(request, ConsultationModel)
    if not consultation:
        return Response(status_code=httpx.codes.BAD_REQUEST)

    site_url = build_consultation_url(consultation.consultation_id)
    trello_url = build_trello_url(consultation.username_trello)

    text = API_CONSULTATION_MESSAGE.format(
        consultation_number=consultation.consultation_number, site_url=site_url, trello_url=trello_url
    )
    await send_message(api.state.bot_app.bot, consultation.telegram_id, text)
    return Response(status_code=httpx.codes.OK)


@requires("authenticated", status_code=401)
async def consultation_feedback(request: Request) -> Response:
    request_data = await deserialize(request, FeedbackConsultationModel)
    if not request_data:
        return Response(status_code=httpx.codes.BAD_REQUEST)

    bot = api.state.bot_app.bot
    text = API_NEW_FEEDBACK.format(consultation_number=request_data.consultation_number, feedback=request_data.feedback)
    await send_message(bot=bot, chat_id=request_data.telegram_id, text=text)
    return Response(status_code=httpx.codes.OK)


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
