from datetime import date

from markupsafe import Markup
from sqlalchemy.orm import RelationshipProperty

from src.models.base import BaseJFModel


def format_date(obj: BaseJFModel, name: str) -> date | str:
    """Задать формат даты."""
    value = getattr(obj, name, None)
    if not value:
        return ''
    return value.strftime('%Y-%m-%d')


def generate_clickable_formatters(
    model: BaseJFModel, details_path: str, column_list: list
) -> dict:
    """Генерирует словарь, делающий поля ссылками на details объекта.

    Словарь передается в атрибут View класса админки column_formatters.
    (ИСКЛЮЧАЕТ relationship поля).
    """
    base_path = details_path.rstrip('/')
    mapper = model.__mapper__
    formatters = {}

    for col in column_list:
        if isinstance(col, str):
            col_name = col
        else:
            col_name = getattr(col, 'key', None) or getattr(col, 'name', None)

        if not col_name or col_name.lower() == 'id':
            continue

        prop = mapper.attrs.get(col_name)
        if isinstance(prop, RelationshipProperty):
            continue
        formatters[col] = lambda obj, attr, cn=col_name: Markup(
            f'<a href="{base_path}/{obj.id}">{getattr(obj, cn)}</a>'
        )

    return formatters
