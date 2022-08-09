# pylint: disable=C0103
from dataclasses import dataclass
from typing import Optional


@dataclass
class UserData:
    username: str
    timezone: str
    username_trello: str


@dataclass
class UserMonthStat:
    closed_consultations: int
    rating: float
    average_user_answer_time: float


@dataclass
class MonthStat(UserMonthStat):
    telegram_id: int
    timezone: str


@dataclass
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


@dataclass
class UserActiveConsultations:
    username_trello: str
    active_consultations: int
    expiring_consultations: int
    expiring_consultations_data: list[dict[str, str]]


@dataclass
class UserExpiredConsultations:
    username_trello: str
    expired_consultations: int
    expired_consultations_data: list[dict[str, str]]


@dataclass
class BillStat:
    telegram_ids: list[int]


@dataclass
class OverdueConsultation:
    id: int
    due: str
    telegram_id: int
    username_trello: str


@dataclass
class DueConsultation:
    due: Optional[str]
