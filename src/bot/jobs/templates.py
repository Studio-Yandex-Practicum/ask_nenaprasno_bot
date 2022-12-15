REMINDER_BASE_TEMPLATE = (
    "[Открыть заявку на сайте]({site_url})\n"
    "----\n"
    "В работе **{active_consultations}** {declination_consultation}\n"
    "Истекает срок у **{expired_consultations}** {genitive_declination_consultation}\n\n"
    "[Открыть Trello]({trello_overdue_url})"
)

DUE_REMINDER_TEMPLATE = (
    "Нееееет! Срок ответа на заявку {consultation_number} истек :(\n" "Мы все очень ждем вашего ответа.\n\n"
) + REMINDER_BASE_TEMPLATE

DUE_HOUR_REMINDER_TEMPLATE = (
    "Час прошел, а наша надежда - нет :)\n" "Ответьте, пожалуйста, на заявку {consultation_number}\n\n"
) + REMINDER_BASE_TEMPLATE

PAST_REMINDER_TEMPLATE = (
    "Время и стекло 😎\n" "Заявка от {created} - **{consultation_number}**\n" "Верим и ждем.\n\n"
) + REMINDER_BASE_TEMPLATE

FORWARD_REMINDER_TEMPLATE = (
    "Пупупууу! Истекает срок ответа по заявке {consultation_number} 🔥\n"
    "У нас еще есть время, чтобы ответить человеку вовремя!\n\n"
) + REMINDER_BASE_TEMPLATE

WEEKLY_STATISTIC_TEMPLATE = (
    "Вы делали добрые дела 7 дней!\n"
    'Посмотрите, как прошла ваша неделя в *"Просто спросить"*\n'
    "Закрыто заявок - *{closed_consultations}*\n"
    "В работе *{active_consultations}* {declination_consultation} за неделю\n\n"
    "Истекает срок у *{expiring_consultations}* {genitive_declination_consultation}\n"
    "У *{expired_consultations}* {genitive_declination_expired} срок истек\n\n"
    "[Открыть Trello]({trello_url})\n\n"
    "Мы рады работать в одной команде :)\n"
    "Так держать!\n"
)

MONTHLY_STATISTIC_TEMPLATE = (
    "Это был отличный месяц!\n"
    'Посмотрите, как он прошел в *"Просто спросить"* 🔥\n\n'
    "Количество закрытых заявок - *{closed_consultations}*\n"
    "{rating}"
    "{average_user_answer_time}\n"
    "[Открыть Trello]({trello_url})\n\n"
    "Мы рады работать в одной команде :)\n"
    "Так держать!\n"
)

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
NATIONAL_DATE_FORMAT = "%d.%m.%Y"  # unused?
