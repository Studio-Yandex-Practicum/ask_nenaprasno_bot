from http import HTTPStatus

import httpx

from core import config
from service.api_client.base import AbstractAPIService
from service.api_client.models import (
    BillStat,
    MonthStat,
    UserActiveConsultations,
    UserData,
    UserExpiredConsultations,
    UserMonthStat,
    WeekStat,
)


class SiteAPIService(AbstractAPIService):
    """
    TODO: development after Frontend API creation
    """

    def __init__(self):
        self.site_url: str = config.SITE_API_URL
        self.bot_token: str = config.SITE_API_BOT_TOKEN

    async def get_bill(self) -> BillStat:
        ...

    async def get_week_stat(self) -> list[WeekStat]:
        url = f"{self.site_url}/tgbot/stat/weekly"
        headers = {"token": self.bot_token}
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers)
            response = await response.json()
            return [
                WeekStat(
                    telegram_id=week_stat["telegram_name"],
                    timezone=week_stat["timezone"],
                    username_trello=week_stat["username_trello"],
                    closed_consultations=week_stat["closed_consultations"],
                    not_expiring_consultations=week_stat["not_expiring_consultations:"],
                    expiring_consultations=week_stat["expiring_consultations"],
                    expired_consultations=week_stat["expired_consultations"],
                    active_consultations=week_stat["active_consultations"],
                    all_consultations=week_stat["all_consultations"],
                )
                for week_stat in response
            ]

    async def get_month_stat(self) -> list[MonthStat]:
        ...

    async def get_user_active_consultations(self, telegram_id: int) -> UserActiveConsultations:
        url = f"{self.site_url}/tgbot/stat/active/user/{telegram_id}"
        active_consultations = await self.__get_data(url=url)
        active_consultations = UserActiveConsultations(**active_consultations)
        return active_consultations

    async def get_user_expired_consultations(self, telegram_id: int) -> UserExpiredConsultations:
        url = f"{self.site_url}/tgbot/stat/overdue/user/{telegram_id}"
        expired_consultations = await self.__get_data(url=url)
        expired_consultations = UserExpiredConsultations(**expired_consultations)
        return expired_consultations

    async def get_user_month_stat(self, telegram_id: int) -> UserMonthStat:
        url = f"{self.site_url}/tgbot/stat/monthly/user/{telegram_id}"
        user_month_stat = await self.__get_data(url=url)
        user_month_stat = UserMonthStat(**user_month_stat)
        return user_month_stat

    async def authenticate_user(self, telegram_id: int) -> UserData | None:
        url = f"{self.site_url}/tgbot/user/{telegram_id}"
        user = await self.__get_data(url=url)
        user = UserData(**user)
        return user

    async def set_user_timezone(self, telegram_id: int, user_time_zone: str) -> HTTPStatus:
        url = f"{self.site_url}/tgbot/user"
        headers = {"Authorization": self.bot_token}
        data = {"telegram_id": telegram_id, "time_zone": user_time_zone}
        async with httpx.AsyncClient() as client:
            response = await client.put(url=url, headers=headers, data=data)
            return response.status_code

    async def __get_data(self, url: str) -> dict:
        headers = {"Authorization": self.bot_token}
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers)
            if response.status_code != HTTPStatus.OK:
                return None
            return response.json()
