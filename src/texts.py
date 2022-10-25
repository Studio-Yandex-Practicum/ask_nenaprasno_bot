from core import config

# common
__JUST_ASK = '"Просто спросить"'
BTN_YES = "Да"
BTN_NO = "Нет"


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
BTN_MONTH_STAT = "Статистика за месяц"
BTN_IN_PROGRESS = "В работе"
BTN_OVERDUE = "🔥 Cроки горят"
BTN_RULES = "Правила сервиса"
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
PLURAL_CONSULTATION = "заявка", "заявки", "заявок"

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
