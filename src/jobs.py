from telegram.ext import CallbackContext

from src.service.send_mailing import send_month_statistic, send_week_statistic


async def weekly_stat_job(context: CallbackContext) -> None:
    """
    Send weekly statistics on the number of requests in the work
    """
    success = await send_week_statistic(context=context)
    if not success:
        # TODO add Logic when send mailing statistic Failed
        pass


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
    success = await send_month_statistic(context=context)
    if not success:
        # TODO add Logic when send mailing statistic Failed
        pass
