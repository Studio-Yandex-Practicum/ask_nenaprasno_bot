from texts.common import __JUST_ASK_NAME, __OPEN_TRELLO_URL

# bot.py
REMIND_IN_NEXT_MONTH = "Не будем напоминать до следующего месяца"


# jobs.py
__TEMPLATE_REMINDER = (
    "[Открыть заявку на сайте]({site_url})\n"
    "----\n"
    "В работе **{active_consultations}** {declination_consultation}\n"
    "Истекает срок у **{expired_consultations}** {genitive_declination_consultation}\n\n"
    f"{__OPEN_TRELLO_URL}"
)

TEMPLATE_DUE_REMINDER = (
    "Нееееет! Срок ответа на заявку {consultation_number} истек :(\nМы все очень ждем вашего ответа.\n\n"
    f"{__TEMPLATE_REMINDER}"
)
TEMPLATE_DUE_HOUR_REMINDER = (
    "Час прошел, а наша надежда - нет :)\nОтветьте, пожалуйста, на заявку {consultation_number}\n\n"
    f"{__TEMPLATE_REMINDER}"
)
TEMPLATE_PAST_REMINDER = (
    "Время и стекло 😎\n" "Заявка от {created} - **{consultation_number}**\nВерим и ждем.\n\n" f"{__TEMPLATE_REMINDER}"
)
TEMPLATE_FORWARD_REMINDER = (
    "Пупупууу! Истекает срок ответа по заявке {consultation_number} 🔥\n"
    "У нас еще есть время, чтобы ответить человеку вовремя!\n\n"
    f"{__TEMPLATE_REMINDER}"
)
__STATISTICS_FOOTER = f"{__OPEN_TRELLO_URL}\n\n" "Мы рады работать в одной команде :)\nТак держать!\n"
TEMPLATE_WEEKLY_STATISTIC = (
    "Вы делали добрые дела 7 дней!\n"
    f"Посмотрите, как прошла ваша неделя в *{__JUST_ASK_NAME}*\n"
    "Закрыто заявок - *{closed_consultations}*\n"
    "В работе *{active_consultations}* {declination_consultation} за неделю\n\n"
    "Истекает срок у *{expiring_consultations}* {genitive_declination_consultation}\n"
    "У *{expired_consultations}* {genitive_declination_expired} срок истек\n\n"
    f"{__STATISTICS_FOOTER}"
)

TEMPLATE_MONTHLY_STATISTIC = (
    "Это был отличный месяц!\n"
    f"Посмотрите, как он прошел в *{__JUST_ASK_NAME}* 🔥\n\n"
    "Количество закрытых заявок - *{closed_consultations}*\n"
    "{rating}\n"
    "{average_user_answer_time}\n\n"
    f"{__STATISTICS_FOOTER}"
)

BILL_REMINDER_TEXT = "Вы активно работали весь месяц! Не забудьте отправить чек нашему кейс-менеджеру"


# run_webhook_api.py
TEMPLATE_NEW_CONSULTATION = (
    "Ура! Вам назначена новая заявка ***{consultation_number}***\n"
    "[Посмотреть заявку на сайте]({site_url})\n---\n"
    "В работе ***{active_cons_count}*** {declination_consultation}\n"
    "Истекает срок у ***{expired_cons_count}*** {genitive_declination_consultation}\n\n"
    f"{__OPEN_TRELLO_URL}\n\n"
)
TEMPLATE_CONSULTATION_MESSAGE = (
    "Вау! Получено новое сообщение в чате заявки ***{consultation_number}***\n"
    "[Прочитать сообщение]({site_url})\n\n"
    f"{__OPEN_TRELLO_URL}"
)
TEMPLATE_NEW_FEEDBACK = (
    "Воу-воу-воу, у вас отзыв!\n"
    "Ваша ***заявка {consultation_number}*** успешно закрыта пользователем!\n\n"
    "***{feedback}***\n\n"
    "Надеемся, он был вам полезен:)"
)
