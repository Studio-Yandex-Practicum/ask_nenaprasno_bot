from telegram import Update
from telegram.ext import ContextTypes

from constants import callback_data
from service.bill import done_bill_callback_handler, skip_bill_callback_handler
from service.repeat_message import repeat_message_after_1_hour_callback


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    callback_message = update.callback_query.data
    match callback_message:
        case callback_data.CALLBACK_REPEAT_COMMAND:
            await repeat_message_after_1_hour_callback(update=update, context=context)
        case callback_data.CALLBACK_DONE_BILL_COMMAND:
            await done_bill_callback_handler(update=update, context=context)
        case callback_data.CALLBACK_SKIP_BILL_COMMAND:
            await skip_bill_callback_handler(update=update, context=context)
