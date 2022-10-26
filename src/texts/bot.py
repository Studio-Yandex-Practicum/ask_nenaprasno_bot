from texts.common import __JUST_ASK, __OPEN_TRELLO

# services/repeat_message.py
BTN_REMIND_IN_HOUR = "🕑 Напомнить через час"


# bot.py
REMIND_IN_NEXT_MONTH = "Не будем напоминать до следующего месяца"


# jobs.py
__REMINDER_BASE_TEMPLATE = (
    "[Открыть заявку на сайте]({site_url})\n"
    "----\n"
    "В работе **{active_consultations}** {declination_consultation}\n"
    "Истекает срок у **{expired_consultations}** {genitive_declination_consultation}\n\n"
    f"{__OPEN_TRELLO}"
)

DUE_REMINDER_TEMPLATE = (
    "Нееееет! Срок ответа на заявку {consultation_number} истек :(\nМы все очень ждем вашего ответа.\n\n"
    f"{__REMINDER_BASE_TEMPLATE}"
)
DUE_HOUR_REMINDER_TEMPLATE = (
    "Час прошел, а наша надежда - нет :)\nОтветьте, пожалуйста, на заявку {consultation_number}\n\n"
    f"{__REMINDER_BASE_TEMPLATE}"
)
PAST_REMINDER_TEMPLATE = (
    "Время и стекло 😎\n"
    "Заявка от {created} - **{consultation_number}**\nВерим и ждем.\n\n"
    f"{__REMINDER_BASE_TEMPLATE}"
)
FORWARD_REMINDER_TEMPLATE = (
    "Пупупууу! Истекает срок ответа по заявке {consultation_number} 🔥\n"
    "У нас еще есть время, чтобы ответить человеку вовремя!\n\n"
    f"{__REMINDER_BASE_TEMPLATE}"
)
__STATISTICS_FOOTER = f"{__OPEN_TRELLO}\n\n" "Мы рады работать в одной команде :)\n" "Так держать!\n"
WEEKLY_STATISTIC_TEMPLATE = (
    "Вы делали добрые дела 7 дней!\n"
    f"Посмотрите, как прошла ваша неделя в *{__JUST_ASK}*\n"
    "Закрыто заявок - *{closed_consultations}*\n"
    "В работе *{active_consultations}* {declination_consultation} за неделю\n\n"
    "Истекает срок у *{expiring_consultations}* {genitive_declination_consultation}\n"
    "У *{expired_consultations}* {genitive_declination_expired} срок истек\n\n"
    f"{__STATISTICS_FOOTER}"
)

MONTHLY_STATISTIC_TEMPLATE = (
    "Это был отличный месяц!\n"
    f"Посмотрите, как он прошел в *{__JUST_ASK}* 🔥\n\n"
    "Количество закрытых заявок - *{closed_consultations}*\n"
    "{rating}\n"
    "{average_user_answer_time}\n\n"
    f"{__STATISTICS_FOOTER}"
)

BILL_REMINDER_TEXT = "Вы активно работали весь месяц! Не забудьте отправить чек нашему кейс-менеджеру"


# run_webhook_api.py
API_NEW_CONSULTATION = (
    "Ура! Вам назначена новая заявка ***{consultation_number}***\n"
    "[Посмотреть заявку на сайте]({site_url})\n---\n"
    "В работе ***{active_cons_count}*** {declination_consultation}\n"
    "Истекает срок у ***{expired_cons_count}*** {genitive_declination_consultation}\n\n"
    f"{__OPEN_TRELLO}\n\n"
)
API_CONSULTATION_MESSAGE = (
    "Вау! Получено новое сообщение в чате заявки ***{consultation_number}***\n"
    "[Прочитать сообщение]({site_url})\n\n"
    f"{__OPEN_TRELLO}"
)
API_NEW_FEEDBACK = (
    "Воу-воу-воу, у вас отзыв!\n"
    "Ваша ***заявка {consultation_number}*** успешно закрыта пользователем!\n\n"
    "***{feedback}***\n\n"
    "Надеемся, он был вам полезен:)"
)
