from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from constants import commands as cmd_const
from constants import messages as msg
from constants import states
from core.config import URL_SERVICE_RULES


async def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton(msg.YES_MESSAGE, callback_data=cmd_const.IS_EXPERT_COMMAND),
            InlineKeyboardButton(msg.NO_MESSAGE, callback_data=cmd_const.NOT_EXPERT_COMMAND),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=msg.START_INVITE_AND_ASK_MESSAGE, reply_markup=reply_markup)
    return states.UNAUTHORIZED_STATE


async def not_expert_callback(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton(msg.YES_MESSAGE, callback_data=cmd_const.REGISTR_AS_EXPERT_COMMAND),
            InlineKeyboardButton(msg.NO_MESSAGE, callback_data=cmd_const.SUPPORT_OR_CONSULT_COMMAND),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(text=msg.NOT_EXPERT_ASK_MESSAGE, reply_markup=reply_markup)
    return states.REGISTRATION_STATE


async def support_or_consult_callback(update: Update, context: CallbackContext):
    return ConversationHandler.END


async def registr_as_expert_callback(update: Update, context: CallbackContext):
    await update.callback_query.message.reply_text(text=msg.INVITE_NEW_EXPERT_MESSAGE)
    return states.NEW_EXPERT_STATE


async def after_registr_message_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(text=msg.NEW_EXPERT_ADDED_AND_SETUP_TIMEZONE_MESSAGE)
    return states.TIMEZONE_STATE


async def is_expert_callback(update: Update, context: CallbackContext):
    return states.TIMEZONE_STATE


async def timezone_callback(update: Update, context: CallbackContext):
    return states.MENU_STATE


async def skip_timezone_callback(update: Update, context: CallbackContext):
    return states.MENU_STATE


async def timezone_message_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        text=msg.TIMEZONE_SETUP_FINISH_MESSAGE, reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        text=msg.HOUSTON_WE_HAVE_A_PROBLEM_MESSAGE, reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    menu_buttons = [
        [
            InlineKeyboardButton(
                text=msg.TIMEZONE_SETUP_MENU_MESSAGE, callback_data=cmd_const.TIMEZONE_CONFIGURATE_COMMAND
            )
        ],
        [
            InlineKeyboardButton(
                text=msg.MONTHLY_STATISTIC_MENU_MESSAGE, callback_data=cmd_const.STATISTIC_MONTH_COMMAND
            )
        ],
        [InlineKeyboardButton(text=msg.WEEKLY_STATISTIC_MENU_MESSAGE, callback_data=cmd_const.STATISTIC_WEEK_COMMAND)],
        [InlineKeyboardButton(text=msg.AT_WORK_MENU_MESSAGE, callback_data=cmd_const.ACTUAL_REQUESTS_COMMAND)],
        [InlineKeyboardButton(text=msg.OVERDUE_MENU_MESSAGE, callback_data=cmd_const.OVERDUE_REQUESTS_COMMAND)],
        [InlineKeyboardButton(text=msg.SERVICE_RULES_MENU_MESSAGE, url=URL_SERVICE_RULES)],
    ]
    await update.message.reply_text(msg.MENU_MESSAGE, reply_markup=InlineKeyboardMarkup(menu_buttons))


async def handling_menu_button_click_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(query.data)


start_command_handler = CommandHandler(cmd_const.START_COMMAND, start)
cancel_command_handler = CommandHandler(cmd_const.CANCEL_COMMAND, cancel)
menu_command_handler = CommandHandler(cmd_const.MENU_COMMAND, menu)

start_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name=msg.START_CONVERSATION_NAME,
    entry_points=[start_command_handler, menu_command_handler],
    states={
        states.UNAUTHORIZED_STATE: [
            CallbackQueryHandler(is_expert_callback, pattern=cmd_const.IS_EXPERT_COMMAND),
            CallbackQueryHandler(not_expert_callback, pattern=cmd_const.NOT_EXPERT_COMMAND),
        ],
        states.REGISTRATION_STATE: [
            CallbackQueryHandler(registr_as_expert_callback, pattern=cmd_const.REGISTR_AS_EXPERT_COMMAND),
            CallbackQueryHandler(support_or_consult_callback, pattern=cmd_const.SUPPORT_OR_CONSULT_COMMAND),
        ],
        states.NEW_EXPERT_STATE: [CallbackQueryHandler(after_registr_message_callback)],
        states.TIMEZONE_STATE: [
            CallbackQueryHandler(timezone_callback, pattern=cmd_const.TIMEZONE_COMMAND),
            CallbackQueryHandler(skip_timezone_callback, pattern=cmd_const.SKIP_TIMEZONE_COMMAND),
            CallbackQueryHandler(timezone_message_callback),
        ],
        states.MENU_STATE: [
            CallbackQueryHandler(handling_menu_button_click_callback, pattern=cmd_const.MENU_COMMAND),
        ],
    },
    fallbacks=[cancel_command_handler],
)
