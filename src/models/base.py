"""Базовые модели проекта."""

from datetime import datetime
from typing import Annotated

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)


unique_str_annotate = Annotated[str, mapped_column(unique=True)]


class BaseJFModel(AsyncAttrs, DeclarativeBase):
    """Базовая модель Joker Fireworks проекта.

    Поля:
        created_at: Дата создания объекта в бд. Автозаполнение.
        updated_at: Дата изменения объекта в бд. Автозаполнение.

    Задает наследникам имя таблицы в бд строчными буквами от названия модели.
    """

    __abstract__ = True

    @declared_attr
    def tablename(cls):  # noqa: N805
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(
            timezone=True,
        ),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(
            timezone=True,
        ),
        server_default=func.now(),
    )
