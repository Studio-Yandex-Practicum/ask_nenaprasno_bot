from dataclasses import dataclass, field

from dataclasses_json import config, dataclass_json


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


@dataclass_json
@dataclass(frozen=True)
class MonthStat:
    telegram_id: int = field(metadata=config(field_name="telegram_name"))
    timezone: str = field(metadata=config(field_name="timezone"))
    closed_consultations: int = field(metadata=config(field_name="closed_consultations"))
    rating: float = field(metadata=config(field_name="rating"))
    average_user_answer_time: float = field(metadata=config(field_name="average_user_answer_time"))


@dataclass_json
@dataclass(frozen=True)
class WeekStat:
    telegram_id: int = field(metadata=config(field_name="telegram_name"))
    timezone: str = field(metadata=config(field_name="timezone"))
    username_trello: str = field(metadata=config(field_name="username_trello"))
    closed_consultations: int = field(metadata=config(field_name="closed_consultations"))
    not_expiring_consultations: int = field(metadata=config(field_name="not_expiring_consultations"))
    expiring_consultations: int = field(metadata=config(field_name="expiring_consultations"))
    expired_consultations: int = field(metadata=config(field_name="expired_consultations"))
    active_consultations: int = field(metadata=config(field_name="active_consultations"))
    all_consultations: int = field(metadata=config(field_name="all_consultations"))


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
