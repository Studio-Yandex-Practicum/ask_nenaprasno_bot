from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackQueryHandler, ConversationHandler,
                          CallbackContext)
from src.constans import (command_constans as cmd_const,
                          constans as const, states)


async def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data='user_expert'),
            InlineKeyboardButton("2", callback_data='not_expert'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        const.GREETING_MESSAGE,
        reply_markup=reply_markup)
    return states.USER_IS_EXPERT


async def user_is_expert(update: Update, context: CallbackContext):
    return states.TIMEZONE


async def timezone(update: Update, context: CallbackContext):
    return states.MENU


async def skip_timezone(update: Update, context: CallbackContext):
    return states.MENU


def main() -> None:
    conv_handler = ConversationHandler(  # noqa
        allow_reentry=True,
        persistent=True,
        name='user_states_handler',
        entry_points=[cmd_const.START_COMMAND_HANDLER],
        states={
            states.USER_IS_EXPERT: [
                CallbackQueryHandler(
                    user_is_expert,
                    pattern=cmd_const.COMMAND_USER_IS_EXPERT
                ),
            ],
            states.TIMEZONE: [
                CallbackQueryHandler(
                    timezone,
                    pattern=cmd_const.COMMAND_TIMEZONE
                ),
                CallbackQueryHandler(
                    skip_timezone,
                    pattern=cmd_const.COMMAND_SKIP_TIMEZONE
                )
            ],
        },
        fallbacks=[
            cmd_const.START_COMMAND_HANDLER,
            cmd_const.MENU_COMMAND_HANDLER],
    )


if __name__ == "__main__":
    main()
