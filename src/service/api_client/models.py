# pylint: disable=C0103
from dataclasses import dataclass
from typing import Optional, Union

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class UserData:
    username: str
    timezone: Union[str, None]
    username_trello: str


@dataclass_json
@dataclass(frozen=True)
class UserMonthStat:
    closed_consultations: int
    rating: Union[float, None]
    average_user_answer_time: Union[float, None]


@dataclass_json
@dataclass(frozen=True)
class MonthStat:
    telegram_id: int
    timezone: str
    username_trello: str
    closed_consultations: int
    rating: float
    average_user_answer_time: float


@dataclass_json
@dataclass(frozen=True)
class WeekStat:
    telegram_id: int
    timezone: str
    username_trello: str
    closed_consultations: int
    not_expiring_consultations: int
    expiring_consultations: int
    expired_consultations: int
    active_consultations: int
    all_consultations: int


@dataclass_json
@dataclass(frozen=True)
class ConsultationData:
    id: str
    number: int


@dataclass_json
@dataclass(frozen=True)
class UserActiveConsultations:
    username_trello: str
    active_consultations: int
    active_consultations_data: list[ConsultationData]


@dataclass_json
@dataclass(frozen=True)
class UserExpiredConsultations:
    username_trello: str
    expired_consultations: int
    expired_consultations_data: list[ConsultationData]


@dataclass_json
@dataclass(frozen=True)
class BillStat:
    telegram_ids: list[int]


@dataclass_json
@dataclass(frozen=True)
class Consultation:
    id: int
    due: str
    telegram_id: int
    username_trello: str


@dataclass_json
@dataclass(frozen=True)
class ConsultationDueDate:
    due: Optional[str]
