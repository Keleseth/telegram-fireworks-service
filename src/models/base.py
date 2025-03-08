"""Базовые модели проекта."""

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr

from src.database.annotations import created_at, updated_at


class BaseJFModel(AsyncAttrs, DeclarativeBase):
    """Базовая модель Joker Fireworks проекта.

    Поля:
        created_at: Дата создания объекта в бд. Автозаполнение.
        updated_at: Дата изменения объекта в бд. Автозаполнение.

    Задает наследникам имя таблицы в бд строчными буквами от названия модели.
    """

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower()

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
