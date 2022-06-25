from telegram import Update
from telegram.ext import ContextTypes

from src.service import ConreateAPIService


async def auth_telegram_user(
    telegram_id: int,
    context: ContextTypes.DEFAULT_TYPE
):
    """context.bot_data[auth_status.user_id_in_trello] = update.effective_chat.id"""
    api_service = ConreateAPIService()
    user_data = await api_service.authenticate_user(telegram_id=telegram_id)
    context.user_data["user_name"] = user_data.user_name
    context.user_data["user_id_in_trello"] = user_data.user_id_in_trello
    context.user_data["user_time_zone"] = user_data.user_time_zone


