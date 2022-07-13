from dataclasses import dataclass


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
    expiring_consultation_ids: list[int]
    expiring_consultation_trello_card_ids: list[int]


@dataclass
class UserExpiredConsultations:
    username_trello: str
    expired_consultations: int
    expired_consultation_ids: list[int]
    expired_consultation_trello_card_ids: list[int]


@dataclass
class BillStat:
    telegram_ids: list[int]
