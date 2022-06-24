from http import HTTPStatus

import httpx

from .api_client_base import APIService
from .api_client_dataclasses import BillStat, MonthStat, UserData, WeekStat


class RealAPIService(APIService):
    async def get_bill(self) -> BillStat:
        url = f"{self.site_url}tgbot/stat/bill"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = response.json()
            return MonthStat(response["telegram_id"])

    async def get_week_stat(self) -> WeekStat:
        url = f"{self.site_url}tgbot/stat/weekly"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = response.json()
            return MonthStat(response["week_stat"])

    async def get_month_stat(self) -> MonthStat:
        url = f"{self.site_url}tgbot/stat/monthly"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = response.json()
            return MonthStat(response["month_stat"])

    async def authenticate_user(self, telegram_id: int) -> UserData:
        url = f"{self.site_url}tgbot/auth"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data={"telegram_id": telegram_id})
            response = response.json()
            return UserData(response["username"], response["user_time_zone"], response["user_id_in_trello"])

    async def set_user_timezone(self, telegram_id: int, user_timezone: int) -> HTTPStatus:
        url = f"{self.site_url}tgbot/user"
        async with httpx.AsyncClient() as client:
            response = await client.put(url, data={"telegram_id": telegram_id, "user_timezone": user_timezone})
            return response.status_code == HTTPStatus.OK
