from typing import TYPE_CHECKING

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.alembic_models import BaseJFModel

if TYPE_CHECKING:
    from src.database.alembic_models import FavoriteFirework


# class PreferedLanguage(str, PyEnum):  # TODO оставляем на реализацию
#     EN = 'english'
#     RU = 'русский'


class User(BaseJFModel, SQLAlchemyBaseUserTableUUID):  # type: ignore[misc]
    """Основная модель пользователя.

    Поля:
        id: UUID айди.
        telegram_id: айди в телеграмме.
        email: почта пользователя.
        age_verified: является ли пользователь совершеннолетним (18+).
        name: имя в телеграмме пользователя.
        nickname: ник в телеграмме пользователя.
        phone_number: телефон пользователя.
        prefered_language: предпочитаемый язык.
        is_admin: является ли пользователь админом.
        is_superuser: является ли пользователь суперадмином.
    """

    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger, unique=True, nullable=True
    )
    email: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True
    )  # type: ignore
    hashed_password: Mapped[str | None] = mapped_column(String, nullable=True)  # type: ignore
    name: Mapped[str] = mapped_column(String, nullable=False)
    nickname: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True
    )
    phone_number: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True
    )
    age_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    # prefered_language: Mapped[PreferedLanguage] = mapped_column(
    #     Enum(PreferedLanguage), default=PreferedLanguage.RU
    # )  # TODO оставляем на реализацию
    favorite_fireworks: Mapped[list['FavoriteFirework']] = relationship(
        back_populates='user'
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = {'extend_existing': True}

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(id={self.id!r}, name={self.name!r}, '
        )
