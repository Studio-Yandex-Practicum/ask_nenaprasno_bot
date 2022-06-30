from telegram import Update
from telegram.ext import ContextTypes

from constants import callback_data
from service.bill import bill_done_callback, skip_callback
from service.repeat_message import repeat_message_after_1_hour_callback


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    callback_message = update.callback_query.data
    match callback_message:
        case callback_data.CALLBACK_REPEAT_COMMAND:
            await repeat_message_after_1_hour_callback(update=update, context=context)
        case callback_data.CALLBACK_BILL_DONE:
            await bill_done_callback(update=update, context=context)
        case callback_data.CALLBACK_BILL_SKIP:
            await skip_callback(update=update, context=context)
