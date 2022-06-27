from http import HTTPStatus

import httpx

from service.api_client.base import AbstractAPIService
from service.api_client.models import BillStat, MonthStat, UserData, UserMonthStat, UserWeekStat, WeekStat


class SiteAPIService(AbstractAPIService):
    async def get_bill(self) -> BillStat:
        url = f"{self.site_url}/tgbot/bill"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = await response.json()
            return WeekStat(response["telegram_name"])

    async def get_week_stat(self) -> list[WeekStat]:
        url = f"{self.site_url}/tgbot/stat/weekly"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = response.json()
            return WeekStat(response["week_stat"])

    async def get_month_stat(self) -> list[MonthStat]:
        url = f"{self.site_url}/tgbot/stat/monthly"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = response.json()
            return WeekStat(response["month_stat"])

    async def get_user_week_stat(self, telegram_name: str) -> UserWeekStat:
        url = f"{self.site_url}/tgbot/stat/weekly/user/{telegram_name}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = response.json()
            return WeekStat(response["week_stat"])

    async def get_user_month_stat(self, telegram_name: str) -> UserMonthStat:
        url = f"{self.site_url}/tgbot/stat/monthly/user/{telegram_name}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = response.json()
            return WeekStat(response["month_stat"])

    async def authenticate_user(self, telegram_name: str) -> UserData | None:
        url = f"{self.site_url}/tgbot/auth"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data={"telegram_name": telegram_name})
            response = response.json()
            return UserData(response["username"], response["user_timezone"], response["user_name_in_trello"])

    async def set_user_timezone(self, telegram_name: str, user_timezone: str) -> HTTPStatus:
        url = f"{self.site_url}/tgbot/user"
        async with httpx.AsyncClient() as client:
            response = await client.put(url, data={"telegram_name": telegram_name, "user_timezone": user_timezone})
            return response.status_code == HTTPStatus.OK
