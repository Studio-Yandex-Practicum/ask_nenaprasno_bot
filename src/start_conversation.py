from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardRemove, Update)
from telegram.ext import (CallbackQueryHandler, ConversationHandler,
                          CommandHandler, ContextTypes, CallbackContext)

from constants import commands, states, texts


async def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton(
                text=texts.YES,
                callback_data=commands.COMMAND_IS_EXPERT
            ),
            InlineKeyboardButton(
                text=texts.NO,
                callback_data=commands.COMMAND_NOT_EXPERT
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text=texts.GREETING,
        reply_markup=reply_markup)
    return states.UNAUTHORIZED_STATE


async def not_expert_callback(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton(
                text=texts.YES,
                callback_data=commands.COMMAND_REGISTR_EXPERT
            ),
            InlineKeyboardButton(
                text=texts.NO,
                callback_data=commands.COMMAND_SUPPORT_OR_CONSULT
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text=texts.WANT_TO_BECOME_AN_EXPERT,
        reply_markup=reply_markup)
    return states.REGISTRATION_STATE


async def support_or_consult_callback(
    update: Update,
    context: CallbackContext
):
    return ConversationHandler.END


async def registr_as_expert_callback(update: Update, context: CallbackContext):
    await update.message.reply_text(
        text=texts.WE_EXITED_TO_ADD_YOU
    )
    return states.NEW_EXPERT_STATE


async def after_registr_message_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        text=texts.AFTER_REGISTER
    )
    return states.TIMEZONE_STATE


async def is_expert_callback(update: Update, context: CallbackContext):
    return states.TIMEZONE_STATE


async def timezone_callback(update: Update, context: CallbackContext):
    return states.MENU_STATE


async def skip_timezone_callback(update: Update, context: CallbackContext):
    return states.MENU_STATE


async def timezone_message_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        text=texts.TIMEZONE_HAS_BEEN_SET,
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text=texts.HOUSTON,
        reply_markup=ReplyKeyboardRemove()
    )
    ConversationHandler.END


start_command_handler = CommandHandler("start", start)
cancel_command_handler = CommandHandler("cancel", cancel)

start_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name="start_conversation",
    entry_points=[start_command_handler],
    states={
        states.UNAUTHORIZED_STATE: [
            CallbackQueryHandler(
                is_expert_callback,
                pattern=commands.COMMAND_IS_EXPERT
            ),
            CallbackQueryHandler(
                not_expert_callback,
                pattern=commands.COMMAND_NOT_EXPERT
            )
        ],
        states.REGISTRATION_STATE: [
            CallbackQueryHandler(
                registr_as_expert_callback,
                pattern=commands.COMMAND_REGISTR_EXPERT
            ),
            CallbackQueryHandler(
                support_or_consult_callback,
                pattern=commands.COMMAND_SUPPORT_OR_CONSULT
            )
        ],
        states.NEW_EXPERT_STATE: [
            CallbackQueryHandler(after_registr_message_callback)
        ],
        states.TIMEZONE_STATE: [
            CallbackQueryHandler(
                timezone_callback,
                pattern=commands.COMMAND_TIMEZONE
            ),
            CallbackQueryHandler(
                skip_timezone_callback,
                pattern=commands.COMMAND_SKIP_TIMEZONE
            ),
            CallbackQueryHandler(timezone_message_callback)
        ],
        states.MENU_STATE: [],
    },
    fallbacks=[cancel_command_handler]
)
