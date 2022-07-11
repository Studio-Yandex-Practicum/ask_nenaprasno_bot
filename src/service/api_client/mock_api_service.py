from http import HTTPStatus
from typing import Optional

from service.api_client.base import AbstractAPIService
from service.api_client.models import BillStat, MonthStat, UserData, UserMonthStat, UserWeekStat, WeekStat


class MockAPIService(AbstractAPIService):
    async def get_bill(self) -> BillStat:
        return BillStat(telegram_ids=[12345685, 78945656, 4564512312])

    async def get_week_stat(self) -> list[WeekStat]:
        return [
            WeekStat(
                telegram_id=971746479,
                timezone="UTC+3",
                username_trello="user1@trello",
                consultations_closed=10,
                consultations_not_expiring=2,
                consultations_expiring=1,
                consultations_expired=1,
                consultations_in_work=4,
                consultations_all=14,
            ),
            WeekStat(
                telegram_id=721889325,
                timezone="UTC+3",
                username_trello="user2@trello",
                consultations_closed=5,
                consultations_not_expiring=3,
                consultations_expiring=2,
                consultations_expired=1,
                consultations_in_work=6,
                consultations_all=16,
            ),
        ]

    async def get_month_stat(self) -> list[MonthStat]:
        return [
            MonthStat(
                telegram_id=971746479,
                timezone="UTC+3",
                consultations_closed=10,
                rating=3.2,
                consultation_resolve_time=4.1,
            ),
            MonthStat(
                telegram_id=721889325,
                timezone="UTC+3",
                consultations_closed=5,
                rating=2.2,
                consultation_resolve_time=5.1,
            ),
        ]

    async def get_user_week_stat(self, telegram_id: int) -> UserWeekStat:
        return UserWeekStat(
            username_trello="user1@telegram",
            consultations_closed=10,
            consultations_not_expiring=2,
            consultations_expiring=1,
            consultations_expired=1,
            consultations_in_work=4,
            consultations_all=14,
        )

    async def get_user_month_stat(self, telegram_id: int) -> UserMonthStat:
        return UserMonthStat(
            consultations_closed=5,
            rating=2.2,
            consultation_resolve_time=5.1,
        )

    async def authenticate_user(self, telegram_id: int) -> Optional[None]:
        return UserData(
            username="Bob",
            timezone="UTC+3",
            username_trello="user1@telegram",
        )

    async def set_user_timezone(self, telegram_id: int, user_time_zone: str) -> HTTPStatus:
        return HTTPStatus.OK
