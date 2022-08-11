from datetime import date, datetime, timedelta
from string import Template

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from constants.callback_data import CALLBACK_DONE_BILL_COMMAND, CALLBACK_SKIP_BILL_COMMAND
from constants.jobs import DATETIME_FORMAT_FOR_DUE_CONSULTATION
from core import config
from core.send_message import send_message, send_statistics
from service.api_client import APIService
from service.repeat_message import repeat_after_one_hour_button


async def weekly_stat_job(context: CallbackContext) -> None:
    """
    Send weekly statistics on the number of requests in the work
    """
    week_statistics = await APIService().get_week_stat()
    template_message = Template(
        "Вы делали добрые дела 7 дней!\n"
        'Посмотрите, как прошла ваша неделя  в *""Просто спросить""*\n'
        "Закрыто заявок - *$closed_consultations*\n"
        "В работе *$active_consultations* заявок  за неделю\n\n"
        "Истекает срок у *$expiring_consultations заявок*\n"
        "У *$expired_consultations* заявок срок истек\n\n"
        "Открыть [Trello](https://trello.com)\n\n"
        "Мы рады работать в одной команде :)\n"
        "*Так держать!*"
    )
    alias_dict = dict(
        closed_consultations="closed_consultations",
        active_consultations="active_consultations",
        expiring_consultations="expiring_consultations",
        expired_consultations="expired_consultations",
    )
    await send_statistics(
        context,
        template_message,
        alias_dict,
        week_statistics,
    )


async def monthly_stat_job(context: CallbackContext) -> None:
    """
    Send monthly statistics on the number of successfully
    closed requests.
    Only if the user had requests
    """
    month_statistics = await APIService().get_month_stat()
    template_message = Template(
        "Это был отличный месяц!\n"
        'Посмотрите, как он прошел в *""Просто спросить""* 🔥\n\n'
        "Количество закрытых заявок - *$closed_consultations*\n"
        "Рейтинг - *$rating*\n"
        "Среднее время ответа - *$average_user_answer_time*\n\n"
        "Открыть [Trello](https://trello.com)\n\n"
        "Мы рады работать в одной команде :)\n"
        "*Так держать!*"
    )
    alias_dict = dict(
        closed_consultations="closed_consultations",
        rating="rating",
        average_user_answer_time="average_user_answer_time",
    )
    await send_statistics(
        context,
        template_message,
        alias_dict,
        month_statistics,
    )


async def monthly_bill_reminder_job(context: CallbackContext) -> None:
    """
    Send monthly reminder about the receipt formation during payment
    Only for self-employed users
    """
    bill_stat = await APIService().get_bill()
    user_list = bill_stat.telegram_ids
    for telegram_id in user_list:
        context.job_queue.run_once(daily_bill_remind_job, when=timedelta(seconds=1), user_id=telegram_id)


async def daily_bill_remind_job(context: CallbackContext) -> None:
    """
    Send message every day until delete job from JobQueue
    :param context:
    :return:
    """
    job = context.job
    message = "Вам необходимо сформировать чек"
    bill_done_button = InlineKeyboardButton(text="✅ Уже отправил(а)", callback_data=CALLBACK_DONE_BILL_COMMAND)
    bill_skip_button = InlineKeyboardButton(text="🕑 Скоро отправлю", callback_data=CALLBACK_SKIP_BILL_COMMAND)
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


async def check_and_send_reminder_about_overdue(context: CallbackContext) -> None:
    """
    Check time overdue consultation and create new job or
    send message to user.
    """
    consultation_id, telegram_id, trello_name = context.job.data
    consultation = await APIService().get_due_consultation(consultation_id)
    if consultation is None:
        return
    if consultation.due is not None:
        due_time = datetime.strptime(consultation.due, DATETIME_FORMAT_FOR_DUE_CONSULTATION)
        if due_time.date() > date.today():
            return
        if due_time > datetime.now() - timedelta(hours=1):
            context.job_queue.run_once(
                check_and_send_reminder_about_overdue,
                when=due_time + timedelta(hours=1),
                data=(
                    consultation_id,
                    telegram_id,
                ),
            )
        else:
            user_active = await APIService().get_user_active_consultations(telegram_id)
            user_expired = await APIService().get_user_expired_consultations(telegram_id)
            message = (
                "Час прошел, а наша надежда - нет 😃\n"
                f"Ответьте пожалуйста на заявку {consultation_id}\n"
                "[Открыть заявку на сайте](https://ask.nenaprasno.ru/)\n\n"
                "----\n"
                f"В работе **{user_active.active_consultations}** заявок\n"
                f"Истекает срок у **{user_expired.expired_consultations}** заявок\n"
                f"[Открыть Trello](https://trello.com/u/{trello_name}/cards)"
            )
            await send_message(chat_id=telegram_id, text=message, context=context)


async def overdue_consult_reminder_job(context: CallbackContext) -> None:
    """
    Makes jobs reminder for overdue consultation today.
    """
    overdue_consultations = await APIService().get_overdue_consultation()
    for consultation in overdue_consultations:
        due_time = datetime.strptime(consultation.due, DATETIME_FORMAT_FOR_DUE_CONSULTATION)
        time_remind = due_time + timedelta(hours=1)
        context.job_queue.run_once(
            check_and_send_reminder_about_overdue,
            when=time_remind,
            data=(
                consultation.id,
                consultation.telegram_id,
                consultation.username_trello,
            ),
        )
