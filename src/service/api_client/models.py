from dataclasses import dataclass


@dataclass
class UserData:
    user_name: str
    user_time_zone: str
    user_name_in_trello: str


@dataclass
class UserWeekStat:
    telegram_name: str
    user_timezone: str
    user_name_in_trello: str
    last_week_user_tikets_in_work: str
    last_week_user_tickets_closed: str
    last_week_user_tickets_expiring: str
    last_week_user_tickets_expired: str


@dataclass
class UserMonthStat:
    user_timezone: str
    user_tickets_closed: str
    user_rating: str
    user_ticket_resolve_avg_time: str


@dataclass
class MyMonthStat:
    user_tickets_closed: str
    user_rating: str
    user_ticket_resolve_avg_time: str


@dataclass
class MyWeekStat:
    user_name_in_trello: str
    last_week_user_tikets_in_work: str
    last_week_user_tickets_closed: str
    last_week_user_tickets_expiring: str
    last_week_user_tickets_expired: str


@dataclass
class WeekStat:
    week_stat: list[UserWeekStat]


@dataclass
class MonthStat:
    month_stat: list[UserMonthStat]


@dataclass
class BillStat:
    telegram_name: list[str]
