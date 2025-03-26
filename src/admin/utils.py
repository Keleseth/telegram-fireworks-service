from datetime import date

from src.models.base import BaseJFModel


def format_date(obj: BaseJFModel, name: str) -> date | str:
    """Задать формат даты."""
    value = getattr(obj, name, None)
    if not value:
        return ''
    return value.strftime('%Y-%m-%d')
