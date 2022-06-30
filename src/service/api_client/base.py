from abc import ABC, abstractmethod
from http import HTTPStatus

from service.api_client.models import BillStat, MonthStat, UserData, UserMonthStat, UserWeekStat, WeekStat


class AbstractAPIService(ABC):
    @abstractmethod
    async def get_bill(self) -> BillStat:
        pass

    @abstractmethod
    async def get_week_stat(self) -> list[WeekStat]:
        pass

    @abstractmethod
    async def get_month_stat(self) -> list[MonthStat]:
        pass

    @abstractmethod
    async def get_user_week_stat(self, telegram_id: int) -> UserWeekStat:
        pass

    @abstractmethod
    async def get_user_month_stat(self, telegram_id: int) -> UserMonthStat:
        pass

    @abstractmethod
    async def authenticate_user(self, telegram_id: int) -> UserData:
        pass

    @abstractmethod
    async def set_user_timezone(
        self, telegram_id: int, user_time_zone: str
    ) -> HTTPStatus:
        pass
