from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import int_pk
from src.models.base import BaseJFModel

if TYPE_CHECKING:
    from src.models.product import Firework


class FireworkDiscount(BaseJFModel):
    """Связующая таблица Many-to-Many между фейерверками и скидками.

    У модели нет id, они служит только как свезующее звено между скидками
    и фейерверками.
    """

    firework_id: Mapped[int] = mapped_column(
        ForeignKey('firework.id', ondelete='CASCADE'), primary_key=True
    )
    discount_id: Mapped[int] = mapped_column(
        ForeignKey('discount.id', ondelete='CASCADE'), primary_key=True
    )


class Discount(BaseJFModel):
    """Модель скидок фейерверков.

    Поля:
        id: int - primary key.
        firework_id: ссылка на модель Firework
        type: тип скидки, процентная, фиксированая, подарочная
        value: сумма скидки или процент.
        start_date: дата начала действия скидки.
        end_date: дата окончания скидки.
        description: описание скидки.
    """

    id: Mapped[int_pk]
    type: Mapped[str]
    value: Mapped[Decimal | None] = mapped_column(
        DECIMAL(10, 2), nullable=True
    )
    start_date: Mapped[datetime]
    end_date: Mapped[datetime]
    description: Mapped[str]

    fireworks: Mapped[list['Firework']] = relationship(
        secondary='fireworkdiscount',
        back_populates='discounts',
    )
