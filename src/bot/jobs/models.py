from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

from bot.jobs import templates
from service.api_client.models import Consultation


@dataclass(frozen=True)
class BaseConsultationData:
    """Stores structured data that is passed
    within a job to the job_queue of the bot.
    """

    consultation: Consultation
    message_template: Optional[str]

    def __get_date(self, prop: str) -> date:
        return datetime.strptime(getattr(self.consultation, prop), templates.DATE_FORMAT).date()

    def due_date(self) -> date:
        return self.__get_date("due")

    def created_date(self) -> date:
        return self.__get_date("created")


@dataclass(frozen=True)
class DueConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    right upon expiration of the due time.
    """

    message_template: str = templates.DUE_REMINDER_TEMPLATE

    def in_valid_time_range(self) -> bool:
        return self.due_date() == datetime.utcnow().date()


@dataclass(frozen=True)
class DueHourConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    one hour after expiration of the due time.
    """

    message_template: str = templates.DUE_HOUR_REMINDER_TEMPLATE

    def in_valid_time_range(self) -> bool:
        return self.due_date() == datetime.utcnow().date()


@dataclass(frozen=True)
class PastConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    for consultations expired at least one day ago.
    """

    message_template: str = templates.PAST_REMINDER_TEMPLATE

    def in_valid_time_range(self) -> bool:
        return self.due_date() < datetime.utcnow().date()


@dataclass(frozen=True)
class ForwardConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    for consultations expiring tomorrow.
    """

    message_template: str = templates.FORWARD_REMINDER_TEMPLATE

    def in_valid_time_range(self) -> bool:
        return self.due_date() - datetime.utcnow().date() == timedelta(days=1)
