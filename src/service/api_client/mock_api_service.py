from http import HTTPStatus
from typing import Optional

from service.api_client.base import AbstractAPIService
from service.api_client.models import (
    BillStat,
    MonthStat,
    UserActiveConsultations,
    UserData,
    UserExpiredConsultations,
    UserMonthStat,
    WeekStat,
)


class MockAPIService(AbstractAPIService):
    async def get_bill(self) -> BillStat:
        return BillStat(telegram_ids=[12345685, 78945656, 4564512312])

    async def get_week_stat(self) -> list[WeekStat]:
        return [
            WeekStat(
                telegram_id=971746479,
                timezone="UTC+3",
                username_trello="user1@trello",
                closed_consultations=10,
                not_expiring_consultations=2,
                expiring_consultations=1,
                expired_consultations=1,
                active_consultations=4,
                all_consultations=14,
            ),
            WeekStat(
                telegram_id=721889325,
                timezone="UTC+3",
                username_trello="user2@trello",
                closed_consultations=5,
                not_expiring_consultations=3,
                expiring_consultations=2,
                expired_consultations=1,
                active_consultations=6,
                all_consultations=11,
            ),
        ]

    async def get_month_stat(self) -> list[MonthStat]:
        return [
            MonthStat(
                telegram_id=971746479,
                timezone="UTC+03:00",
                closed_consultations=10,
                rating=3.2,
                average_user_answer_time=4.1,
            ),
            MonthStat(
                telegram_id=721889325,
                timezone="UTC+05:00",
                closed_consultations=5,
                rating=2.2,
                average_user_answer_time=5.1,
            ),
        ]

    async def get_user_active_consultations(self, telegram_id: int) -> Optional[UserActiveConsultations]:
        return UserActiveConsultations(
            username_trello="user1@telegram",
            active_consultations=6,
            expiring_consultations=2,
            expiring_consultations_data=[{"consultation_id": "test1", "consultation_trello_card_id": "1_tr"}],
        )
        
    async def get_user_expired_consultations(self, telegram_id: int) -> Optional[UserExpiredConsultations]:
        return UserExpiredConsultations(
            username_trello="user1@telegram",
            expired_consultations=2,
            expired_consultations_data=[{"consultation_id": "test1", "consultation_trello_card_id": "1_tr"}],
        )

    async def get_user_month_stat(self, telegram_id: int) -> Optional[UserMonthStat]:
        return UserMonthStat(
            closed_consultations=5,
            rating=2.2,
            average_user_answer_time=5.1,
        )

    async def authenticate_user(self, telegram_id: int) -> Optional[UserData]:
        return UserData(
            username="Bob",
            timezone="UTC+03:00",
            username_trello="user1@telegram",
        )

    async def set_user_timezone(self, telegram_id: int, user_time_zone: str) -> HTTPStatus:
        return HTTPStatus.OK
