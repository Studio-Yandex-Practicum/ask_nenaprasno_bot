# pylint: disable=no-member
import json
from typing import Optional
from urllib.parse import urljoin

import httpx

from core import config
from core.logger import logger
from service.api_client.base import AbstractAPIService
from service.api_client.models import (
    BillStat,
    Consultation,
    ConsultationDueDate,
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

    async def get_week_stat(self) -> Optional[list[WeekStat]]:
        url = urljoin(self.site_url, "/tgbot/stat/weekly")
        list_week_stat = await self.__get_json_data(url=url)
        try:
            return [WeekStat.from_dict(one_week_stat) for one_week_stat in list_week_stat]
        except TypeError as error:
            logger.error("Failed convert json to dataclass: %s, error: %s", WeekStat, error)
            return None

    async def get_month_stat(self) -> Optional[list[MonthStat]]:
        url = urljoin(self.site_url, "/tgbot/stat/monthly")
        list_month_stat = await self.__get_json_data(url=url)
        try:
            return [MonthStat.from_dict(one_month_stat) for one_month_stat in list_month_stat]
        except TypeError as error:
            logger.error("Failed convert json to dataclass: %s, error: %s", MonthStat, error)
            return None

    async def get_user_active_consultations(self, telegram_id: int) -> Optional[UserActiveConsultations]:
        url = urljoin(self.site_url, f"/tgbot/stat/active/user/{telegram_id}")
        active_consultations = await self.__get_json_data(url=url)
        try:
            return UserActiveConsultations.from_dict(active_consultations)
        except (AttributeError, KeyError) as error:
            logger.error("Failed convert json to dataclass: %s, error: %s", UserActiveConsultations, error)
            return None

    async def get_user_expired_consultations(self, telegram_id: int) -> Optional[UserExpiredConsultations]:
        url = urljoin(self.site_url, f"/tgbot/stat/overdue/user/{telegram_id}")
        exp_consultations = await self.__get_json_data(url=url)
        try:
            return UserExpiredConsultations.from_dict(exp_consultations)
        except (AttributeError, KeyError) as error:
            logger.error("Failed convert json to dataclass: %s, error: %s", UserExpiredConsultations, error)
            return None

    async def get_user_month_stat(self, telegram_id: int) -> Optional[UserMonthStat]:
        url = urljoin(self.site_url, f"/tgbot/stat/monthly/user/{telegram_id}")
        user_month_stat = await self.__get_json_data(url=url)
        try:
            return UserMonthStat.from_dict(user_month_stat)
        except (AttributeError, KeyError) as error:
            logger.error("Failed convert json to dataclass: %s, error: %s", UserMonthStat, error)
            return None

    async def authenticate_user(self, telegram_id: int) -> Optional[UserData]:
        url = urljoin(self.site_url, f"/tgbot/user/{telegram_id}")
        user = await self.__get_json_data(url=url)
        try:
            return UserData.from_dict(user)
        except (AttributeError, KeyError) as error:
            logger.error("Failed convert json to dataclass: %s, error: %s", UserData, error)
            return None

    async def set_user_timezone(self, telegram_id: int, user_time_zone: str) -> Optional[int]:
        url = urljoin(self.site_url, "/tgbot/user")
        headers = {"Authorization": self.bot_token}
        data = {"telegram_id": telegram_id, "timezone": user_time_zone}
        async with httpx.AsyncClient() as client:
            response = await client.put(url=url, headers=headers, json=data)
            return response.status_code

    async def get_daily_consultations(self) -> Optional[list[Consultation]]:
        url = urljoin(self.site_url, "/tgbot/consultations")
        consultations = await self.__get_json_data(url=url)
        try:
            return [Consultation.from_dict(consultation) for consultation in consultations]
        except TypeError as error:
            logger.error("Failed convert json to dataclass: %s", error)
            return None

    async def get_consultation(self, consultation_id: int) -> Optional[ConsultationDueDate]:
        url = urljoin(self.site_url, f"/tgbot/consultations/{consultation_id}")
        consultation = await self.__get_json_data(url=url)
        try:
            return ConsultationDueDate.from_dict(consultation)
        except TypeError as error:
            logger.error("Failed convert json to dataclass: %s", error)
            return None

    async def __get_json_data(self, url: str) -> Optional[dict]:
        headers = {"Authorization": self.bot_token}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url=url, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as error:
                logger.error("Failed get data from server: %s", error)
            except json.JSONDecodeError as error:
                logger.error(
                    "Got a JSONDecodeError in responce decode - %s, url - %s, error - %s", response.text, url, error
                )
            return None
