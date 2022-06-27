from abc import ABC, abstractmethod
from http import HTTPStatus

from core import config
from service.api_client_dataclasses import BillStat, MonthStat, UserData, WeekStat


class APIService(ABC):
    def __init__(self):
        self.site_url = config.SITE_API_URL

    @abstractmethod
    async def get_bill(self) -> BillStat:
        pass

    @abstractmethod
    async def get_week_stat(self) -> WeekStat:
        pass

    @abstractmethod
    async def get_month_stat(self) -> MonthStat:
        pass

    @abstractmethod
    async def authenticate_user(self, telegram_id: int) -> UserData | None:  # если неавторизированный пользователь
        pass

    @abstractmethod
    async def set_user_timezone(self, telegram_id: int, user_timezone: str) -> HTTPStatus:
        pass
