from dataclasses import dataclass


@dataclass
class UserData:
    username: str
    timezone: str
    username_trello: str


@dataclass
class WeekStat:
    telegram_id: int
    timezone: str
    username_trello: str
    consultations_closed: int
    consultations_not_expiring: int
    consultations_expiring: int
    consultations_expired: int
    consultations_in_work: int
    consultations_all: int


@dataclass
class MonthStat:
    telegram_id: int
    timezone: str
    consultations_closed: int
    rating: float
    consultation_resolve_time: float


@dataclass
class UserMonthStat:
    consultations_closed: int
    rating: float
    consultation_resolve_time: float


@dataclass
class UserWeekStat:
    username_trello: str
    consultations_closed: int
    consultations_not_expiring: int
    consultations_expiring: int
    consultations_expired: int
    consultations_in_work: int
    consultations_all: int


@dataclass
class BillStat:
    telegram_ids: list[int]
