from telegram.ext import ContextTypes

from src.service import ConreateAPIService


async def auth_telegram_user(telegram_id: int, context: ContextTypes.DEFAULT_TYPE):
    """
    try to authenticate telegram user on site API and write trello_id to persistence file
    :param telegram_id: user's id from telegram
    :param context: context
    :return: status of authentication
    """
    api_service = ConreateAPIService()
    user_data = await api_service.authenticate_user(telegram_id=telegram_id)
    if user_data is None:
        return False
    context.user_data["user_name"] = user_data.user_name
    context.user_data["user_id_in_trello"] = user_data.user_id_in_trello
    context.user_data["user_time_zone"] = user_data.user_time_zone
    return True
