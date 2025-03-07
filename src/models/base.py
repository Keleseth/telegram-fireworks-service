"""Базовые модели проекта."""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (DeclarativeBase, Mapped, declared_attr,
                            mapped_column)


class BaseJFModel(AsyncAttrs, DeclarativeBase):
    """Базовая модель Joker Fireworks проекта.

    Поля:
        created_at: Дата создания объекта в бд. Автозаполнение.
        updated_at: Дата изменения объекта в бд. Автозаполнение.

    Задает наследникам имя таблицы в бд строчными буквами от названия модели.
    """

    abstract = True

    @declared_attr.directive
    def tablename(cls) -> str:  # noqa: N805
        return cls.__name__.lower()

    created_at: Mapped[datetime] = mapped_column(
        type=TIMESTAMP(
            timezone=True,
        ),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        type=TIMESTAMP(
            timezone=True,
        ),
        server_default=func.now(),
    )
