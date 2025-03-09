from enum import Enum as PyEnum

from .base import BaseJFModel


class PreferedLanguage(str, PyEnum):
    EN = 'english'
    RU = 'русский'


class User(BaseJFModel):
    """Основная модель пользователя.

    Поля:
        id: обычный айди.
        telegram_id: айди в телеграмме.
        email: почта пользователя.
        age_verifid: являестя ли пользователь совершенно летним(18+).
        name: имя в телеграмме пользователь.
        nickname: ник в телеграмме пользователя.
        phone_number: телефон пользователя.
        prefered_language: предпочитаемый язык.
        is_admin: является ли пользователь админом.
        is_superuser: является ли пользователь суперадмином.
    """
