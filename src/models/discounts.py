from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.alembic_models import BaseJFModel
from src.database.annotations import int_pk

if TYPE_CHECKING:
    from src.database.alembic_models import Firework


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

    firework: Mapped['Firework'] = relationship(back_populates='discounts')
    firework_discounts: Mapped['Discount'] = relationship(
        back_populates='fireworks'
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
    value: Mapped[float]
    start_date: Mapped[datetime]
    end_date: Mapped[datetime]
    description: Mapped[str]

    fireworks: Mapped[list['FireworkDiscount']] = relationship(
        back_populates='firework_discounts',
    )
