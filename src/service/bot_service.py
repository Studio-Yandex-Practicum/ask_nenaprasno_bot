import httpx
from starlette.responses import Response
from telegram import Bot

from core.send_message import send_message
from service.models import ConsultationModel, FeedbackConsultationModel


class BotNotifierService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def consultation_feedback(self, request_data: FeedbackConsultationModel) -> Response:
        text = (
            f"Воу-воу-воу, у вас отзыв!\n"
            f"Ваша ***заявка {request_data.consultation_number}*** успешно закрыта пользователем!\n\n"
            f"***{request_data.feedback}***\n\n"
            f"Надеемся, он был вам полезен:)"
        )
        await send_message(self.bot, request_data.telegram_id, text)
        return Response(status_code=httpx.codes.OK)

    async def consultation_message(self, request_data: ConsultationModel) -> Response:
        pass
