from abc import ABC, abstractmethod
from http import HTTPStatus

from core import config
from service.api_client.models import BillStat, MonthStat, UserData, UserMonthStat, UserWeekStat, WeekStat


class AbstractAPIService(ABC):
    site_url: str = config.SITE_API_URL

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
    async def get_user_week_stat(self, telegram_name: str) -> UserWeekStat:
        pass

    @abstractmethod
    async def get_user_month_stat(self, telegram_name: str) -> UserMonthStat:
        pass

    @abstractmethod
    async def authenticate_user(self, telegram_name: str) -> UserData:
        pass

    @abstractmethod
    async def set_user_timezone(self, telegram_name: str, user_timezone: str) -> HTTPStatus:
        pass
