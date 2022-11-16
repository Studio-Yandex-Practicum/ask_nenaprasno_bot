from urllib.parse import urljoin

from core.config import TRELLO_BORD_ID, URL_ASK_NENAPRASNO


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

    return urljoin("https://trello.com/b/", TRELLO_BORD_ID) + f"/?filter={trello_filter}"


def build_consultation_url(consultation_id: str) -> str:
    return urljoin(URL_ASK_NENAPRASNO, f"/consultation/redirect/{consultation_id}")
