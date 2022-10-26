from core import config

# common
__JUST_ASK = '"Просто спросить"'
BTN_YES = "Да"
BTN_NO = "Нет"
BTN_MONTH_STAT = "Статистика за месяц"
BTN_IN_PROGRESS = "В работе"
BTN_OVERDUE = "🔥 Cроки горят"
BTN_RULES = "Правила сервиса"


# conversation/authorization.py
__ONLY_FOR_EXPERTS = f"Этот бот предназначен только для экспертов справочной службы {__JUST_ASK}."
BOT_GREETINGS_MESSAGE = (
    f"Вы успешно начали работу с ботом. Меня зовут Женя Краб, я telegram-bot для экспертов справочной службы "
    f"{__JUST_ASK}.\n"
    "Я буду сообщать вам о новых заявках, присылать уведомления о новых сообщениях в чате от пациентов и их близких и "
    "напоминать о просроченных заявках.\n"
    "Нам нравится, что вы с нами. Не терпится увидеть вас в деле!"
)
BOT_QUESTON_YOU_ARE_EXPERT = (
    f"Привет! Этот бот предназначен только для экспертов справочной службы {__JUST_ASK}.\nВы являетесь экспертом?"
)
BOT_QUESTON_WANT_BE_EXPERT = (
    f"{__ONLY_FOR_EXPERTS}\nХотите стать нашим экспертом и отвечать на заявки от пациентов и их близких?"
)
BOT_OFFER_ONLINE_CONSULTATION = (
    f"{__ONLY_FOR_EXPERTS}\n"
    f"Если у вас возникли вопросы об онкологическом заболевании, заполните заявку на странице справочной службы "
    f"{__JUST_ASK}."
)
BOT_OFFER_FILL_FORM_FOR_FUTURE_EXPERT = (
    "Мы всегда рады подключать к проекту новых специалистов!\n"
    "Здорово, что вы хотите работать с нами.\n"
    f"Заполните, пожалуйста, эту [анкету]({config.FORM_URL_FUTURE_EXPERT}) (нужно 15 минут). Команда сервиса подробно "
    f"изучит вашу заявку и свяжется с вами в течение недели, чтобы договориться о видеоинтервью.\n"
    "Перед интервью мы можем попросить вас ответить на тестовый кейс, чтобы обсудить его на встрече."
)
BOT_OFFER_SEND_TELEGRAM_ID = (
    "Ваш Telegram-идентификатор - ```{telegram_id}```\n\n"
    "Для дальнейшей работы, пожалуйста, перешлите это сообщение кейс-менеджеру, чтобы начать получать уведомления."
)
BTN_CONSULTATION = "Получить онлайн-консультацию"
BTN_SUPPORT = "Поддержать проект"


# conversation/menu.py
BTN_TIMEZONE = "Настроить часовой пояс (сейчас {user_tz})"
BTN_MENU = "Меню"

OVERDUE_TEMPLATE = (
    "Время и стекло 😎\n"
    "Ваше количество просроченных заявок - {expired_consultations}\n"
    "Верим и ждем.\n\n"
    "{link_nenaprasno}\n"
    "----\n"
    "В работе количество заявок - {active_consultations}\n"
    "[Открыть Trello]({trello_url})\n\n"
)

ACTUAL_TEMPLATE = (
    "У вас в работе {active_consultations} {declination_consultation}.\n"
    "{link_nenaprasno}\n"
    "[Открыть Trello]({trello_url})\n\n"
)

PLURAL_DAY = "день", "дня", "дней"
PLURAL_HOUR = "час", "часа", "часов"
PLURAL_CONSULTATION_NOT_SINGLE = "заявки", "заявок"
PLURAL_CONSULTATION = "заявка", *PLURAL_CONSULTATION_NOT_SINGLE

AVERAGE_ANSWER_TIME = "***Среднее время ответа*** - {days} {output_days} {hours} {output_hours}"
RATING = "***Рейтинг*** - {rating:.1f}"
DATA_NOT_AVAILABLE = "Данные недоступны!"

MONTH_STAT_GOOD = (
    f"С начала месяца вы сделали очень много для {__JUST_ASK} 🔥\n"
    "***Количество закрытых заявок*** - {closed_consultations}\n"
    "{rating}\n"
    "{average_answer_time}\n\n"
    "Мы рады работать в одной команде :)\n"
    "Так держать!"
)
MONTH_STAT_BAD = "К сожалению у вас не было отвеченных заявок :(\nМы верим, что в следующем месяце все изменится! :)"

CONSULTATION_LIST_HEAD = "Посмотреть заявки на сайте:"
CONSULTATION_LIST_ITEM = "{number}. [Заявка {consultation_number}]({consultations_url})"


# conversation/timezone.py
BTN_GEOLOCATION = "Отправить свою геолокацию для автоматической настройки часового пояса"
BTN_TIMEZONE_DEFAULT = "Таймзона по умолчанию UTC+03:00 (Москва)."
BTN_TIMEZONE_BY_LOCATION_OR_MANUAL = "Таймзона по локации или вручную."

__TIMEZONE_HELP = (
    "Вот возможные варианты для Москвы:\n"
    "UTC+03:00\n"
    "utc3:0\n"
    "3:0\n"
    "+3\n"
    "3\n"
    "Подробнее о часовых поясах РФ можно почитать на [Википедии](https://ru.wikipedia.org/wiki/Время_в_России)"
)

TIMEZONE_MESSAGE = (
    f"Расшарьте геолокацию или напишите свою таймзону в любом формате относительно часового пояса UTC. "
    f"{__TIMEZONE_HELP}"
)
TIMEZONE_FAIL_MESSAGE = f"Не удалось определить часовой пояс. Пожалуйста, введите его вручную. {__TIMEZONE_HELP}"
TIMEZONE_SUCCESS_MESSAGE = "Вы настроили часовой пояс *{timezone}*, теперь уведомления будут приходить в удобное время."
MENU_HELP__ = "А еще с помощью меня вы можете узнать про:"
TIMEZONE_START = "Для начала, давайте настроим часовой пояс, чтобы вы получали уведомления в удобное время."


# services/repeat_message.py
BTN_REMIND_IN_HOUR = "🕑 Напомнить через час"


# bot.py
REMIND_IN_NEXT_MONTH = "Не будем напоминать до следующего месяца"


# jobs.py
BTN_BILL_SENT = "✅ Уже отправил(а)"
BTN_BILL_SOON = "🕑 Скоро отправлю"

__REMINDER_BASE_TEMPLATE = (
    "[Открыть заявку на сайте]({site_url})\n"
    "----\n"
    "В работе **{active_consultations}** {declination_consultation}\n"
    "Истекает срок у **{expired_consultations}** {genitive_declination_consultation}\n\n"
    "[Открыть Trello]({trello_overdue_url})"
)

DUE_REMINDER_TEMPLATE = (
    "Нееееет! Срок ответа на заявку {consultation_number} истек :(\n" "Мы все очень ждем вашего ответа.\n\n"
) + __REMINDER_BASE_TEMPLATE

DUE_HOUR_REMINDER_TEMPLATE = (
    "Час прошел, а наша надежда - нет :)\n" "Ответьте, пожалуйста, на заявку {consultation_number}\n\n"
) + __REMINDER_BASE_TEMPLATE

PAST_REMINDER_TEMPLATE = (
    "Время и стекло 😎\n" "Заявка от {created} - **{consultation_number}**\n" "Верим и ждем.\n\n"
) + __REMINDER_BASE_TEMPLATE

FORWARD_REMINDER_TEMPLATE = (
    "Пупупууу! Истекает срок ответа по заявке {consultation_number} 🔥\n"
    "У нас еще есть время, чтобы ответить человеку вовремя!\n\n"
) + __REMINDER_BASE_TEMPLATE

WEEKLY_STATISTIC_TEMPLATE = (
    "Вы делали добрые дела 7 дней!\n"
    f"Посмотрите, как прошла ваша неделя в *{__JUST_ASK}*\n"
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
    f"Посмотрите, как он прошел в *{__JUST_ASK}* 🔥\n\n"
    "Количество закрытых заявок - *{closed_consultations}*\n"
    "{rating}\n"
    "{average_user_answer_time}\n\n"
    "[Открыть Trello]({trello_url})\n\n"
    "Мы рады работать в одной команде :)\n"
    "Так держать!\n"
)

BILL_REMINDER_TEXT = "Вы активно работали весь месяц! Не забудьте отправить чек нашему кейс-менеджеру"


# menu_button.py
BTN_START = "Начать работу с ботом."
BTN_MENU2 = "Показать список возможных запросов."


# run_webhook_api.py
API_NEW_CONSULTATION = (
    "Ура! Вам назначена новая заявка ***{consultation_number}***\n"
    "[Посмотреть заявку на сайте]({site_url})\n---\n"
    "В работе ***{active_cons_count}*** {declination_consultation}\n"
    "Истекает срок у ***{expired_cons_count}*** {genitive_declination_consultation}\n\n"
    "[Открыть Trello]({trello_url})\n\n"
)
API_CONSULTATION_MESSAGE = (
    "Вау! Получено новое сообщение в чате заявки ***{consultation_number}***\n"
    "[Прочитать сообщение]({site_url})\n\n"
    "[Открыть Trello]({trello_url})"
)
API_NEW_FEEDBACK = (
    "Воу-воу-воу, у вас отзыв!\n"
    "Ваша ***заявка {consultation_number}*** успешно закрыта пользователем!\n\n"
    "***{feedback}***\n\n"
    "Надеемся, он был вам полезен:)"
)
