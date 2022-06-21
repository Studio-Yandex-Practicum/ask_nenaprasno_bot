from abc import ABC, abstractmethod
from http import HTTPStatus

import httpx

from api_client_dataclasses import (
    UserData, MonthStat, UserMonthStat,
    WeekStat, UserWeekStat, BillStat
)

from core import config


class APIService(ABC):

    def __init__(self):
        self.SITE_URL = config.SITE_URL

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
    async def authenticate_user(self, telegram_id: int) -> UserData:
        pass

    @abstractmethod
    async def set_user_timezone(
        self,
        telegram_id: int,
        user_timezone: str
    ) -> bool:
        pass


class FakeAPIService(APIService):

    async def get_bill(self) -> BillStat:
        return BillStat([
         147892,
         147983,
         147894
        ])

    async def get_week_stat(self) -> WeekStat:
        return WeekStat([
            UserWeekStat(
                147892,
                'UTC+3',
                '24',
                2,
                3,
                2,
                1,
                1
            ),
            UserWeekStat(
                147895,
                'UTC+4',
                '25',
                3,
                4,
                2,
                1,
                1
            )
        ])

    async def get_month_stat(self) -> MonthStat:
        return MonthStat([
            UserMonthStat(
                147890,
                'UTC+3',
                6,
                8,
                9.4,
                4.3
            ),
            UserMonthStat(
                147895,
                'UTC+4',
                6,
                3,
                6.4,
                7.3
            )
        ])

    async def authenticate_user(self, telegram_id: int) -> UserData:
        return UserData(
            'Bob',
            'UTC+3',
            '24'
        )

    async def set_user_timezone(
        self,
        telegram_id: int,
        user_timezone: str
    ) -> httpx.Response:
        return True


class RealAPIService(APIService):

    async def get_bill(self) -> BillStat:
        url = f"{self.SITE_URL}tgbot/stat/bill"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = response.json()
            return MonthStat(response['telegram_id'])

    async def get_week_stat(self) -> WeekStat:
        url = f"{self.SITE_URL}tgbot/stat/weekly"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = response.json()
            return MonthStat(response['week_stat'])

    async def get_month_stat(self) -> MonthStat:
        url = f"{self.SITE_URL}tgbot/stat/monthly"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = response.json()
            return MonthStat(response['month_stat'])

    async def authenticate_user(self, telegram_id: int) -> UserData:
        url = f"{self.SITE_URL}tgbot/auth"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={
                    'telegram_id': telegram_id
                }
            )
            response = response.json()
            return UserData(
                response['username'],
                response['user_time_zone'],
                response['user_id_in_trello']
            )

    async def set_user_timezone(
        self,
        telegram_id: int,
        user_timezone: str
    ) -> bool:
        url = f"{self.SITE_URL}tgbot/user"
        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                data={
                    'telegram_id': telegram_id,
                    'user_timezine': user_timezone
                }
            )
            if response.status_code == HTTPStatus.OK:
                return True
            return False
