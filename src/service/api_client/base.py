from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Optional

from service.api_client.models import (
    BillStat,
    DueConsultation,
    MonthStat,
    OverdueConsultation,
    UserActiveConsultations,
    UserData,
    UserExpiredConsultations,
    UserMonthStat,
    WeekStat,
)


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
    async def get_user_active_consultations(self, telegram_id: int) -> Optional[UserActiveConsultations]:
        pass

    @abstractmethod
    async def get_user_expired_consultations(self, telegram_id: int) -> Optional[UserExpiredConsultations]:
        pass

    @abstractmethod
    async def get_user_month_stat(self, telegram_id: int) -> Optional[UserMonthStat]:
        pass

    @abstractmethod
    async def authenticate_user(self, telegram_id: int) -> Optional[UserData]:
        pass

    @abstractmethod
    async def set_user_timezone(self, telegram_id: int, user_time_zone: str) -> HTTPStatus:
        pass

    @abstractmethod
    async def get_daily_consultations(self) -> list[OverdueConsultation]:
        pass

    @abstractmethod
    async def get_consultation(self, consultation_id: int) -> DueConsultation:
        pass
