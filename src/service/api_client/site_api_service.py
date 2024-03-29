# pylint: disable=no-member
import json
from typing import Dict, Optional
from urllib.parse import urljoin

import httpx

from core.config import settings
from core.logger import log_response, logger
from service.api_client import base, models


class SiteAPIService(base.AbstractAPIService):
    def __init__(self):
        self.site_url: str = settings.url_ask_nenaprasno_api
        self.bot_token: str = settings.site_api_bot_token

    async def get_bill(self) -> Optional[models.BillStat]:
        url = urljoin(self.site_url, "/tgbot/bill")
        users = await self.__get_json_data(url)
        if users is None:
            return None
        return models.BillStat.from_dict(users)

    async def get_week_stat(self) -> Optional[list[models.WeekStat]]:
        url = urljoin(self.site_url, "/tgbot/stat/weekly")
        list_week_stat = await self.__get_json_data(url=url)
        if list_week_stat is None:
            return None
        return [models.WeekStat.from_dict(one_week_stat) for one_week_stat in list_week_stat]

    async def get_month_stat(self) -> Optional[list[models.MonthStat]]:
        url = urljoin(self.site_url, "/tgbot/stat/monthly")
        list_month_stat = await self.__get_json_data(url=url)
        if list_month_stat is None:
            return None
        return [models.MonthStat.from_dict(one_month_stat) for one_month_stat in list_month_stat]

    async def get_user_active_consultations(self, telegram_id: int) -> Optional[models.UserActiveConsultations]:
        url = urljoin(self.site_url, f"tgbot/stat/active/user/{telegram_id}")
        active_consultations = await self.__get_json_data(url=url)
        if active_consultations is None:
            return None
        return models.UserActiveConsultations.from_dict(active_consultations)

    async def get_user_expired_consultations(self, telegram_id: int) -> Optional[models.UserExpiredConsultations]:
        url = urljoin(self.site_url, f"/tgbot/stat/overdue/user/{telegram_id}")
        exp_consultations = await self.__get_json_data(url=url)
        if exp_consultations is None:
            return None
        return models.UserExpiredConsultations.from_dict(exp_consultations)

    async def get_consultations_count(self, telegram_id: int) -> Dict[str, int]:
        """Gets count of active, expiring and expired consultations and returns it in dict.
        keys ['active_consultations_count', 'expiring_consultations_count', 'expired_consultations_count']"""
        active_cons = await self.get_user_active_consultations(telegram_id=telegram_id)
        return {
            "active_consultations_count": active_cons.active_consultations,
            "expiring_consultations_count": active_cons.expiring_consultations,
            "expired_consultations_count": (
                await self.get_user_expired_consultations(telegram_id=telegram_id)
            ).expired_consultations,
        }

    async def get_user_month_stat(self, telegram_id: int) -> Optional[models.UserMonthStat]:
        url = urljoin(self.site_url, f"/tgbot/stat/monthly/user/{telegram_id}")
        user_month_stat = await self.__get_json_data(url=url)
        if user_month_stat is None:
            return None
        return models.UserMonthStat.from_dict(user_month_stat)

    async def authenticate_user(self, telegram_id: int) -> Optional[models.UserData]:
        url = urljoin(self.site_url, f"/tgbot/user/{telegram_id}")
        user = await self.__get_json_data(url=url)
        if user is None:
            return None
        return models.UserData.from_dict(user)

    async def set_user_timezone(self, telegram_id: int, user_time_zone: str) -> Optional[int]:
        url = urljoin(self.site_url, "/tgbot/user")
        headers = {"Authorization": self.bot_token}
        data = {"telegram_id": telegram_id, "timezone": user_time_zone}
        async with httpx.AsyncClient(event_hooks={"response": [log_response]}) as client:
            response = await client.put(url=url, headers=headers, json=data)
            return response.status_code

    async def get_daily_consultations(self) -> Optional[list[models.Consultation]]:
        url = urljoin(self.site_url, "tgbot/consultations/")
        consultations = await self.__get_json_data(url=url)
        if consultations is None:
            return None
        return [models.Consultation.from_dict(consultation) for consultation in consultations]

    async def get_consultation(self, consultation_id: str) -> Optional[models.ConsultationDueDate]:
        url = urljoin(self.site_url, f"tgbot/consultations/{consultation_id}")
        consultation = await self.__get_json_data(url=url)
        if consultation is None:
            return None
        return models.ConsultationDueDate.from_dict(consultation)

    async def __get_json_data(self, url: str) -> Optional[dict]:
        headers = {"Authorization": self.bot_token}
        async with httpx.AsyncClient(event_hooks={"response": [log_response]}) as client:
            try:
                response = await client.get(url=url, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as error:
                logger.error("Failed get data from %s: %s", url, error)
            except json.JSONDecodeError as error:
                logger.error(
                    "Got a JSONDecodeError in responce decode - %s, url - %s, error - %s", response.text, url, error
                )
            return None
