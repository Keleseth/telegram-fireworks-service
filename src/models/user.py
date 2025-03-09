import uuid
from enum import Enum as PyEnum

from sqlalchemy import UUID, BigInteger, Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

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

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger, unique=True, nullable=True
    )
    email: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True
    )
    age_verifid: Mapped[bool] = mapped_column(Boolean, default=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    nickname: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True
    )
    phone_number: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True
    )
    prefered_language: Mapped[PreferedLanguage] = mapped_column(
        Enum(PreferedLanguage), default=PreferedLanguage.RU
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
