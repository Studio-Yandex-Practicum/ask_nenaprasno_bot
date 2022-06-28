from dataclasses import dataclass


@dataclass
class UserData:
    user_name: str
    user_time_zone: str
    user_id_in_trello: str


@dataclass
# pylint: disable=R0902
class UserWeekStat:
    telegram_id: int
    user_timezone: str
    user_id_in_trello: str
    week_num: int
    last_week_user_tikets_in_work: int
    last_week_user_tickets_closed: int
    last_week_user_tickets_expiring: int
    last_week_user_tickets_expired: int


@dataclass
class UserMonthStat:
    telegram_id: int
    user_timezone: str
    month: int
    user_tickets_closed: int
    user_rating: float
    user_ticket_resolve_avg_time: float


@dataclass
class WeekStat:
    week_stat: list[UserWeekStat]


@dataclass
class MonthStat:
    month_stat: list[UserMonthStat]


@dataclass
class BillStat:
    telegram_id: list[int]
