import httpx

from core import config
from service.api_client.base import AbstractAPIService
from service.api_client.models import BillStat, MonthStat, UserData, UserMonthStat, UserWeekStat, WeekStat


class SiteAPIService(AbstractAPIService):
    def __init__(self):
        self.site_url: str = config.SITE_API_URL

    async def get_bill(self) -> BillStat:
        """
        url = f"{self.site_url}/tgbot/bill"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = await response.json()
            return response["telegrame_name"]
        """

    async def get_week_stat(self) -> list[WeekStat]:
        url = f"{self.site_url}/tgbot/stat/weekly"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = await response.json()
            return [
                WeekStat(
                    telegram_name=week_stat["telegram_name"],
                    user_timezone=week_stat["user_timezone"],
                    user_name_in_trello=week_stat["user_name_in_trello"],
                    last_week_user_tickets_closed=week_stat["last_week_user_tickets_closed"],
                    last_week_user_tickets_not_expring=week_stat["last_week_user_tickets_not_expring"],
                    last_week_user_tickets_expiring=week_stat["last_week_user_tickets_expiring"],
                    last_week_user_tickets_expired=week_stat["last_week_user_tickets_expired"],
                    last_week_user_tickets_in_work=week_stat["last_week_user_tickets_in_work"],
                    last_week_user_tickets_all=week_stat["last_week_user_tickets_all"],
                )
                for week_stat in response
            ]

    async def get_month_stat(self) -> list[MonthStat]:
        """
        url = f"{self.site_url}/tgbot/stat/monthly"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = await response.json()
            return [
                MonthStat(
                    telegram_name=month_stat["telegram_name"],
                    user_timezone=month_stat["user_timezone"],
                    user_tickets_closed=month_stat["user_tickets_closed"],
                    user_rating=month_stat["user_rating"],
                    user_ticket_resolve_avg_time=month_stat["user_ticket_resolve_avg_time"],
                )
                for month_stat in response
            ]
        """

    async def get_user_week_stat(self, telegram_name: str) -> UserWeekStat:
        """
        url = f"{self.site_url}/tgbot/stat/weekly/user/{telegram_name}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = await response.json()
            return UserWeekStat(
                user_name_in_trello=response["user_name_in_trello"],
                last_week_user_tickets_closed=response["last_week_user_tickets_closed"],
                last_week_user_tickets_not_expring=response["last_week_user_tickets_not_expring"],
                last_week_user_tickets_expiring=response["last_week_user_tickets_expiring"],
                last_week_user_tickets_expired=response["last_week_user_tickets_expired"],
                last_week_user_tickets_in_work=response["last_week_user_tickets_in_work"],
                last_week_user_tickets_all=response["last_week_user_tickets_all"],
            )
        """

    async def get_user_month_stat(self, telegram_name: str) -> UserMonthStat:
        """
        url = f"{self.site_url}/tgbot/stat/monthly/user/{telegram_name}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response = await response.json()

            return UserMonthStat(
                user_tickets_closed=response["user_tickets_closed"],
                user_rating=response["user_rating"],
                user_ticket_resolve_avg_time=response["user_ticket_resolve_avg_time"],
            )
        """

    async def authenticate_user(self, telegram_name: str) -> UserData | None:
        """
        url = f"{self.site_url}/tgbot/auth"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data={"telegram_name": telegram_name})
            response = await response.json()
            return UserData(
                user_name=response["username"],
                user_time_zone=response["user_timezone"],
                user_name_in_trello=response["user_name_in_trello"],
            )
        """

    async def set_user_timezone(self, telegram_name: str, user_timezone: str) -> httpx:
        """
        url = f"{self.site_url}/tgbot/user"
        async with httpx.AsyncClient() as client:
            response = await client.put(url, data={"telegram_name": telegram_name, "user_timezone": user_timezone})
            return response.status_code == httpx.codes.OK
        """
