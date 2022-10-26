from core import config
from texts.common import __JUST_ASK_NAME, __OPEN_TRELLO_URL

# conversation/authorization.py
__BOT_ONLY_FOR_EXPERTS = f"Этот бот предназначен только для экспертов справочной службы {__JUST_ASK_NAME}."
MESSAGE_GREETINGS = (
    f"Вы успешно начали работу с ботом. Меня зовут Женя Краб, я telegram-bot для экспертов справочной службы "
    f"{__JUST_ASK_NAME}.\n"
    "Я буду сообщать вам о новых заявках, присылать уведомления о новых сообщениях в чате от пациентов и их близких и "
    "напоминать о просроченных заявках.\n"
    "Нам нравится, что вы с нами. Не терпится увидеть вас в деле!"
)
MESSAGE_ARE_YOU_AN_EXPERT = (
    f"Привет! Этот бот предназначен только для экспертов справочной службы {__JUST_ASK_NAME}.\nВы являетесь экспертом?"
)
MESSAGE_WANNA_BE_AN_EXPERT = (
    f"{__BOT_ONLY_FOR_EXPERTS}\nХотите стать нашим экспертом и отвечать на заявки от пациентов и их близких?"
)
MESSAGE_OFFER_ONLINE_CONSULTATION = (
    f"{__BOT_ONLY_FOR_EXPERTS}\n"
    f"Если у вас возникли вопросы об онкологическом заболевании, заполните заявку на странице справочной службы "
    f"{__JUST_ASK_NAME}."
)
MESSAGE_OFFER_FILL_FORM_FOR_EXPERT = (
    "Мы всегда рады подключать к проекту новых специалистов!\n"
    "Здорово, что вы хотите работать с нами.\n"
    f"Заполните, пожалуйста, эту [анкету]({config.FORM_URL_FUTURE_EXPERT}) (нужно 15 минут). Команда сервиса подробно "
    f"изучит вашу заявку и свяжется с вами в течение недели, чтобы договориться о видеоинтервью.\n"
    "Перед интервью мы можем попросить вас ответить на тестовый кейс, чтобы обсудить его на встрече."
)
TEMPLATE_OFFER_SEND_TELEGRAM_ID = (
    "Ваш Telegram-идентификатор - ```{telegram_id}```\n\n"
    "Для дальнейшей работы, пожалуйста, перешлите это сообщение кейс-менеджеру, чтобы начать получать уведомления."
)


# conversation/menu.py
TEMPLATE_OVERDUE = (
    "Время и стекло 😎\n"
    "Ваше количество просроченных заявок - {expired_consultations}\n"
    "Верим и ждем.\n\n"
    "{link_nenaprasno}\n"
    "----\n"
    "В работе количество заявок - {active_consultations}\n"
    f"{__OPEN_TRELLO_URL}\n\n"
)

TEMPLATE_ACTUAL = (
    "У вас в работе {active_consultations} {declination_consultation}.\n"
    "{link_nenaprasno}\n"
    f"{__OPEN_TRELLO_URL}\n\n"
)

USER_AVERAGE_ANSWER_TIME = "***Среднее время ответа*** - {days} {output_days} {hours} {output_hours}"
USER_RATING = "***Рейтинг*** - {rating:.1f}"

TEMPLATE_MONTH_POSITIVE_STAT = (
    f"С начала месяца вы сделали очень много для {__JUST_ASK_NAME} 🔥\n"
    "***Количество закрытых заявок*** - {closed_consultations}\n"
    "{rating}\n"
    "{average_answer_time}\n\n"
    "Мы рады работать в одной команде :)\n"
    "Так держать!"
)
TEMPLATE_MONTH_NEGATIVE_STAT = (
    "К сожалению у вас не было отвеченных заявок :(\nМы верим, что в следующем месяце все изменится! :)"
)

CONSULTATION_LIST_HEAD = "Посмотреть заявки на сайте:"
TEMPLATE_CONSULTATION_LIST_ITEM = "{number}. [Заявка {consultation_number}]({consultations_url})"


# conversation/timezone.py
__TIMEZONE_HELP = (
    "Вот возможные варианты для Москвы:\n"
    "UTC+03:00\n"
    "utc3:0\n"
    "3:0\n"
    "+3\n"
    "3\n"
    "Подробнее о часовых поясах РФ можно почитать на [Википедии](https://ru.wikipedia.org/wiki/Время_в_России)"
)

MESSAGE_TIMEZONE = (
    f"Расшарьте геолокацию или напишите свою таймзону в любом формате относительно часового пояса UTC. "
    f"{__TIMEZONE_HELP}"
)
MESSAGE_TIMEZONE_FAIL = f"Не удалось определить часовой пояс. Пожалуйста, введите его вручную. {__TIMEZONE_HELP}"
TEMPLATE_TIMEZONE_SUCCESS = (
    "Вы настроили часовой пояс *{timezone}*, теперь уведомления будут приходить в удобное время."
)
MENU_HELP__ = "А еще с помощью меня вы можете узнать про:"
MESSAGE_TIMEZONE_START = "Для начала, давайте настроим часовой пояс, чтобы вы получали уведомления в удобное время."
