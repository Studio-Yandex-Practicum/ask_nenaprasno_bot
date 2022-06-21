import zoneinfo

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters
from timezonefinder import TimezoneFinder

# from api_client import set_user_timezone
from constants import text_constants
from core import config


async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            KeyboardButton(
                "Отправить свою геолокацию для автоматической настройки часового пояса", request_location=True
            )
        ],
        [KeyboardButton("Напишу свою таймзону сам")],
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Для начала, давайте настроим часовой пояс, чтобы вы получали уведомления в удобное время",
        reply_markup=markup,
    )


async def get_timezone(update: Update, context: CallbackContext):
    if update.message.location is not None:
        user_timezone = TimezoneFinder().timezone_at(
            lng=update.message.location.longitude, lat=update.message.location.latitude
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Установлен часовой пояс "{user_timezone}"',
            reply_markup=ReplyKeyboardRemove(),
        )
        # set_user_timezone(
        #     telegram_id=update.effective_chat.id,
        #     user_timezone=user_timezone
        # )


async def selected_text(update: Update, context: CallbackContext) -> None:
    try:
        zoneinfo.ZoneInfo(str(update.message.text))
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Установлен часовой пояс {update.message.text}",
            reply_markup=ReplyKeyboardRemove(),
        )
        # set_user_timezone(
        #     telegram_id=update.effective_chat.id,
        #     user_timezone=user_timezone
        # )
    except zoneinfo.ZoneInfoNotFoundError:
        if str(update.message.text) not in text_constants.RHETORICAL_TEXT:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f'Часового пояса "{update.message.text}" нет. Попробуйте'
                    " написать другой или передайте геолокацию для его автоматического"
                    " определения."
                ),
            )


async def weekly_stat_job(context: CallbackContext) -> None:
    """
    Send weekly statistics on the number of requests in the work
    """


async def monthly_receipt_reminder_job(context: CallbackContext) -> None:
    """
    Send monthly reminder about the receipt formation during payment
    Only for self-employed users
    """


async def monthly_stat_job(context: CallbackContext) -> None:
    """
    Send monthly statistics on the number of successfully
    closed requests.
    Only if the user had requests
    """


def create_bot():
    """
    Create telegram bot application
    :return: Created telegram bot application
    """
    bot_app = ApplicationBuilder().token(config.TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT, selected_text))
    bot_app.add_handler(MessageHandler(filters.LOCATION, get_timezone))
    bot_app.job_queue.run_daily(weekly_stat_job, time=config.WEEKLY_STAT_TIME, days=config.WEEKLY_STAT_WEEK_DAYS)
    bot_app.job_queue.run_monthly(
        monthly_receipt_reminder_job, when=config.MONTHLY_RECEIPT_REMINDER_TIME, day=config.MONTHLY_RECEIPT_REMINDER_DAY
    )
    bot_app.job_queue.run_monthly(monthly_stat_job, when=config.MONTHLY_STAT_TIME, day=config.MONTHLY_STAT_DAY)
    return bot_app


async def init_webhook() -> Application:
    """
    Init bot webhook
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.updater = None
    await bot_app.bot.set_webhook(url=f"{config.WEBHOOK_URL}/telegram")
    return bot_app


def init_polling() -> None:
    """
    Init bot polling
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.run_polling()
