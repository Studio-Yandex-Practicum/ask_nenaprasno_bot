from urllib.parse import urljoin

from core.config import settings


def get_word_case(number, single, few, many):
    num = number % 100
    if 5 <= num <= 20:
        return many
    num = number % 10
    if num == 1:
        return single
    if 2 <= num <= 4:
        return few
    return many


def get_word_genitive(number, single, many):
    num = number % 100
    if 2 <= num <= 20:
        return many
    num = number % 10
    if num == 1:
        return single
    return many


def build_trello_url(username_trello: str, overdue: bool = False) -> str:
    trello_filter = f"member:{username_trello}"
    if overdue:
        trello_filter += ",overdue:true"

    return urljoin("https://trello.com/b/", settings.trello_bord_id) + f"/?filter={trello_filter}"


def build_consultation_url(consultation_id: str) -> str:
    return urljoin(settings.url_ask_nenaprasno, f"/consultation/redirect/{consultation_id}")
