from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ContextTypes

from constants.callback_data import CALLBACK_BILL_DONE_COMMAND, CALLBACK_BILL_SKIP_COMMAND
from core import config
from core.send_message import send_message
from service.repeat_message import repeat_after_one_hour_button


async def daily_bill_remind_job(context: CallbackContext) -> None:
    """
    Send message every day until delete job from JobQueue
    :param context:
    :return:
    """
    job = context.job
    message = "Вам необходимо сформировать чек"
    bill_done_button = InlineKeyboardButton(text="✅ Уже отправил(а)", callback_data=CALLBACK_BILL_DONE_COMMAND)
    bill_skip_button = InlineKeyboardButton(text="🕑 Скоро отправлю", callback_data=CALLBACK_BILL_SKIP_COMMAND)
    menu = InlineKeyboardMarkup([[repeat_after_one_hour_button], [bill_done_button], [bill_skip_button]])
    await send_message(chat_id=job.user_id, text=message, reply_markup=menu, context=context)
    send_time = config.MONTHLY_RECEIPT_REMINDER_TIME
    # user_utc = context.user_data.get("UTC")
    # Не смог понять, в каком виде хранятся данные о часовом поясе юзера. Здесь надо переопределить информацию о
    # времени отправки сообщения
    # if user_utc:
    #     send_time += user_utc

    context.job_queue.run_daily(
        daily_bill_remind_job,
        time=send_time,
        user_id=job.user_id,
        name=f"send_{job.user_id}_bill_until_complete",
    )


async def bill_done_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Delete job from JobQueue
    """
    query = update.callback_query
    user_id = query.from_user.id
    current_jobs = context.job_queue.get_jobs_by_name(f"send_{user_id}_bill_until_complete")
    for job in current_jobs:
        job.schedule_removal()
    await query.edit_message_text(text="Не будем напоминать до следующего месяца")
    await query.answer()  # close progress bar in chat


async def skip_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete button under message"""
    query = update.callback_query
    data = query.message
    await query.edit_message_text(text=data.text_markdown_v2_urled)
    await query.answer()  # close progress bar in chat
