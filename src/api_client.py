from abc import ABC, abstractmethod
from http import HTTPStatus

import httpx

from api_client_dataclasses import UserData
from core import config

# метод get_stat обрабатывает все возможные url
# по получению статистики get запросами.
# Правильный ли это подход, или необходимо писать
# по методу на каждую url?
# Если можно ограничится одним методом,
# то неясно какие даные отдавать в фейковом клиенте?
# UserMonthStat или WeekStat, имеет ли это какое-то значение?


class APIService(ABC):

    # @abstractmethod
    # async def get_stat(self):
    #     pass

    @abstractmethod
    async def authenticate_user(self, telegram_id: int) -> bool:
        pass

    @abstractmethod
    async def set_user_timezone(
        self,
        telegram_id: int,
        user_timezone: str
    ) -> bool:
        pass


class FakeAPIService(APIService):

    async def authenticate_user(self, telegram_id: int) -> UserData:
        response = httpx.Response(
            status_code=200,
            json={
                'username': 'Bob',
                'user_time_zone': 'UTC+3',
                'user_id_in_trello': 24
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
    ) -> httpx.Response:
        response = httpx.Response(
            status_code=201
        )
        return response.status_code


class RealAPIService(APIService):

    def __init__(self):
        self.SITE_URL = config.SITE_URL
        self.authentication_code = config.authentication_code  # Другой Таск

    async def authenticate_user(self, telegram_id: int) -> bool:
        url = f"{self.SITE_URL}/tgbot/auth"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={
                    'telegram_id': telegram_id
                }
            )
            if response.status_code == HTTPStatus.OK:
                return True
            return False

    async def set_user_timezone(
        self,
        telegram_id: int,
        user_timezone: str
    ) -> bool:
        url = f"{self.SITE_URL}/tgbot/user"
        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                data={
                    'telegram_id': telegram_id,
                    'user_timezine': user_timezone
                }
            )
            if response.status_code == HTTPStatus.CREATED:
                return True
            return False


class SiteAPIService(APIService):

    def __init__(self, api_service: APIService) -> None:
        self._api_service = api_service
    # def __init__(self) -> None:
    #     if(config.mock_server):
    #         self._api_service = FakeAPIService()
    #     else:
    #         self._api_service = RealAPIService()

    async def authenticate_user(self, telegram_id: int) -> bool:
        return await self._api_service.authenticate_user(telegram_id)

    async def set_user_timezone(
        self,
        telegram_id: int,
        user_timezone: str
    ) -> bool:
        return await self._api_service.set_user_timezone(
            telegram_id,
            user_timezone
        )
