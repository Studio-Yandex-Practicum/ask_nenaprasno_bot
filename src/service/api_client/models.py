from dataclasses import dataclass


@dataclass
class UserData:
    user_name: str
    user_time_zone: str
    user_name_in_trello: str


@dataclass
class WeekStat:
    telegram_name: str
    user_timezone: str
    user_name_in_trello: str
    last_week_user_tickets_closed: int
    last_week_user_tickets_not_expring: int
    last_week_user_tickets_expiring: int
    last_week_user_tickets_expired: int
    last_week_user_tickets_in_work: int
    last_week_user_tickets_all: int


@dataclass
class MonthStat:
    telegram_name: str
    user_timezone: str
    user_tickets_closed: int
    user_rating: float
    user_ticket_resolve_avg_time: float


@dataclass
class UserMonthStat:
    user_tickets_closed: int
    user_rating: float
    user_ticket_resolve_avg_time: float


@dataclass
class UserWeekStat:
    user_name_in_trello: str
    last_week_user_tickets_closed: int
    last_week_user_tickets_not_expring: int
    last_week_user_tickets_expiring: int
    last_week_user_tickets_expired: int
    last_week_user_tickets_in_work: int
    last_week_user_tickets_all: int


@dataclass
class BillStat:
    telegram_name: list[str]
