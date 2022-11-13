from typing import Dict, Tuple

from starlette.responses import Response
from telegram.ext import Application

from core import utils
from core.send_message import send_message
from service.models import (
    AssignedConsultationModel,
    ClosedConsultationModel,
    ConsultationModel,
    FeedbackConsultationModel,
)


class BotNotifierService:
    """Класс работы с приложением бота"""

    def __init__(self, bot_app: Application):
        self.__bot_app = bot_app

    async def consultation_assignment(
        self, request_data: AssignedConsultationModel, consultations_count: Dict[str, int]
    ) -> Response:
        """Отправка информации при назначении новой заявки"""
        active_consultations_count = consultations_count["active_consultations_count"]
        expired_consultations_count = consultations_count["expired_consultations_count"]
        expiring_consultations_count = consultations_count["expiring_consultations_count"]
        declination_consultation = utils.get_word_case(active_consultations_count, "заявка", "заявки", "заявок")
        genitive_declination_consultation_expiring = utils.get_word_genitive(
            expiring_consultations_count, "заявки", "заявок"
        )
        genitive_declination_consultation_expired = utils.get_word_genitive(
            expired_consultations_count, "заявки", "заявок"
        )

        site_url = utils.build_consultation_url(request_data.consultation_id)
        trello_url = utils.build_trello_url(request_data.username_trello)

        text = (
            f"Ура! Вам назначена новая заявка ***{request_data.consultation_number}***\n"
            f"[Посмотреть заявку на сайте]({site_url})\n"
            "---\n"
            f"В работе ***{active_consultations_count}*** {declination_consultation}\n"
            f"Истекает срок у ***{expiring_consultations_count}*** {genitive_declination_consultation_expiring}\n"
            f"Истек срок у ***{expired_consultations_count}*** {genitive_declination_consultation_expired}\n"
            f"\n"
            f"[Открыть Trello]({trello_url})\n\n"
        )
        await send_message(self.__bot_app.bot, request_data.telegram_id, text)

    async def consultation_feedback(self, request_data: FeedbackConsultationModel) -> Response:
        """Отправка отзыва на консультацию в чат бота"""
        text = (
            f"Воу-воу-воу, у вас отзыв!\n"
            f"Ваша ***заявка {request_data.consultation_number}*** успешно закрыта пользователем!\n\n"
            f"***{request_data.feedback}***\n\n"
            f"Надеемся, он был вам полезен:)"
        )
        await send_message(self.__bot_app.bot, request_data.telegram_id, text)

    async def consultation_message(self, request_data: ConsultationModel) -> Response:
        """Отправка информации о новом сообщения по консультации в чате"""
        site_url = utils.build_consultation_url(request_data.consultation_id)
        trello_url = utils.build_trello_url(request_data.username_trello)

        text = (
            f"Вау! Получено новое сообщение в чате заявки ***{request_data.consultation_number}***\n"
            f"[Прочитать сообщение]({site_url})\n"
            f"\n"
            f"[Открыть Trello]({trello_url})"
        )
        await send_message(self.__bot_app.bot, request_data.telegram_id, text)

    def consultation_close(self, request_data: ClosedConsultationModel) -> Response:
        """Удаление из очереди джобов, относящися к закрытой консультации"""
        consultation_id = request_data.consultation_id
        reminder_jobs = self.__bot_app.job_queue.jobs()
        for job in reminder_jobs:
            if isinstance(job.data, Tuple) and job.data[0] == consultation_id:
                job.schedule_removal()
