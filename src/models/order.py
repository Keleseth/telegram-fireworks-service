from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import int_pk
from src.models.base import BaseJFModel

if TYPE_CHECKING:
    from src.models.address import UserAddress
    from src.models.product import Firework
    from src.models.user import User

FIREWORK_PRICE_NUMBER_OF_DIGITS = 10
FIREWORK_PRICE_FRACTIONAL_PART = 2


class OrderStatus(Enum):
    CREATED = 'created'
    PAID = 'paid'
    PENDING = 'pending'


class Order(BaseJFModel):
    """Модель заказа."""

    id: Mapped[int_pk]
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('user.id'), nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), nullable=False
    )
    user_address_id: Mapped[int | None] = mapped_column(
        ForeignKey('useraddress.id', ondelete='SET NULL'), nullable=True
    )

    user: Mapped['User'] = relationship('User', back_populates='orders')
    user_address: Mapped['UserAddress' | None] = relationship(
        'UserAddress', back_populates='orders'
    )
    fireworks: Mapped[list['Firework']] = relationship(
        'Firework', secondary='orderfirework', back_populates='orders'
    )


class OrderFirework(BaseJFModel):
    """Связь товаров и заказов."""

    order_id: Mapped[int] = mapped_column(
        ForeignKey('order.id', ondelete='CASCADE'), nullable=False
    )
    firework_id: Mapped[int] = mapped_column(
        ForeignKey('firework.id', ondelete='SET NULL'), nullable=True
    )
    amount: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    price_per_unit: Mapped[Numeric] = mapped_column(
        Numeric(
            FIREWORK_PRICE_NUMBER_OF_DIGITS, FIREWORK_PRICE_FRACTIONAL_PART
        ),
        nullable=False,
    )

    order: Mapped['Order'] = relationship(
        back_populates='fireworks', cascade='all, delete'
    )
    firework: Mapped['Firework'] = relationship(
        'Firework', back_populates='order_fireworks'
    )
