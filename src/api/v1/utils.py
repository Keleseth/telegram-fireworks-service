"""Модуль для вспомогательных инструментов."""

from math import ceil
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


def build_next_and_prev_urls(
    offset: int, limit: int, objects_count: int, current_url: str
) -> tuple[str]:
    """Обновляет Query-параметры url для пагинации.

    Аргументы:
        offset (int): сдвиг выборки.
        limit (int): количество объектов на странице.
        objects_count (int): полное количество объектов в БД.
        current_url (str): текущий url-адрес.

    Возвращаемое значение:
        tuple[str, int]: кортеж с ссылками на предыдущую
            и следующую страницы и с количеством страниц.
    """
    parsed_url = urlparse(current_url)
    query_params = parse_qs(parsed_url.query)
    query_params['offset'] = [str(offset + limit)]
    query_params['limit'] = [str(limit)]
    next_page_url = (
        urlunparse(
            parsed_url._replace(query=urlencode(query_params, doseq=True))
        )
        if offset + limit < objects_count
        else None
    )
    query_params['offset'] = [str(max(offset - limit, 0))]
    query_params['limit'] = [str(limit)]
    previous_page_url = (
        urlunparse(
            parsed_url._replace(query=urlencode(query_params, doseq=True))
        )
        if offset > 0
        else None
    )
    return previous_page_url, next_page_url, ceil(objects_count / limit)
