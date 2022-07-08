import httpx

from core import config
from service.api_client.base import AbstractAPIService
from service.api_client.models import BillStat, MonthStat, UserData, UserMonthStat, UserWeekStat, WeekStat


class SiteAPIService(AbstractAPIService):
    """
    TODO: development after Frontend API creation
    """

    def __init__(self):
        self.site_url: str = config.SITE_API_URL
        self.bot_token: str = config.SITE_API_BOT_TOKEN

    async def get_bill(self) -> BillStat:
        pass

    async def get_week_stat(self) -> list[WeekStat]:
        url = f"{self.site_url}/tgbot/stat/weekly"
        headers = {"token": self.bot_token}
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers)
            response = await response.json()
            return [
                WeekStat(
                    telegram_id=week_stat["telegram_name"],
                    timezone=week_stat["user_timezone"],
                    username_trello=week_stat["username_trello"],
                    consultations_closed=week_stat["consultations_closed"],
                    consultations_not_expiring=week_stat["consultations_not_expiring"],
                    consultations_expiring=week_stat["consultations_expiring"],
                    consultations_expired=week_stat["consultations_expired"],
                    consultations_in_work=week_stat["consultations_in_work"],
                    consultations_all=week_stat["consultations_all"],
                )
                for week_stat in response
            ]

    async def get_month_stat(self) -> list[MonthStat]:
        pass

    async def get_user_week_stat(self, telegram_id: int) -> UserWeekStat:
        pass

    async def get_user_month_stat(self, telegram_id: int) -> UserMonthStat:
        pass

    async def authenticate_user(self, telegram_id: int) -> UserData | None:
        pass

    async def set_user_timezone(self, telegram_id: int, user_time_zone: str) -> httpx:
        pass
