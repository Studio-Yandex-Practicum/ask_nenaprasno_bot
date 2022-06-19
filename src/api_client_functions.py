import httpx

from abc import ABC, abstractmethod


from api_client_dumpdata import (
    TGBOT_STAT_MONTHLY_USER, TGBOT_AUTH
)


class APICallServiceBase(ABC):
    def __init__(self, base_url):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    @abstractmethod
    async def get(self):
        pass

    @abstractmethod
    async def post(self):
        pass

    @abstractmethod
    async def put(self):
        pass


class APICallService(APICallServiceBase):
    async def get(self, url):
        request = await self.client.get(self.base_url + url)
        return request

    async def post(self, url, **kwargs):
        request = await self.client.post(self.base_url + url, **kwargs)
        return request

    async def put(self, url, **kwargs):
        request = await self.client.put(self.base_url + url, **kwargs)
        return request


class APICallServiceDUMB(APICallServiceBase):
    def get(self, url):
        response = httpx.Response(
            status_code=200,
            json=TGBOT_STAT_MONTHLY_USER
        )
        return response

    def post(self, url, **kwargs):
        response = httpx.Response(
            status_code=200,
            json=TGBOT_AUTH
        )
        return response

    def put(self, url, **kwargs):
        response = httpx.Response(
            status_code=201
        )
        return response


class SiteService:
    def __init__(self, api_service):
        self.api_service = api_service

    async def get_stat(self, endpoint):
        request = self.api_service.get(endpoint)
        data = request.json()
        return data

    async def authenticate_user(self, endpoint, telegram_id):
        data = {
            'telegram_id': telegram_id
        }
        request = self.api_service.post(endpoint, data=data)
        data = request.json()
        return data

    async def set_user_timezone(self, endpoint, telegram_id, user_timezone):
        data = {
            'telegram_id': telegram_id,
            'user_timezone': user_timezone
        }
        request = self.api_service.put(endpoint, data=data)
        return request.status_code
