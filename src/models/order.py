from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import int_pk
from src.models.base import BaseJFModel

if TYPE_CHECKING:
    from src.models.address import UserAddress
    from src.models.product import Firework
    from src.models.user import User

FIREWORK_PRICE_NUMBER_OF_DIGITS = 10
FIREWORK_PRICE_FRACTIONAL_PART = 2


class OrderStatus(BaseJFModel):
    id: Mapped[int_pk]
    status_text: Mapped[str]


class Order(BaseJFModel):
    id: Mapped[int_pk]
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('user.id'), nullable=False
    )
    status_id: Mapped['OrderStatus'] = mapped_column(
        ForeignKey('orderstatus.id'), nullable=False
    )
    user_address_id: Mapped[int | None] = mapped_column(
        ForeignKey('useraddress.id', ondelete='SET NULL'), nullable=True
    )
    fio: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    operator_call: Mapped[bool] = mapped_column(default=False, nullable=False)
    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default='0.00'
    )

    user: Mapped['User'] = relationship(
        back_populates='orders', lazy='selectin'
    )
    user_address: Mapped[Optional['UserAddress']] = relationship(
        back_populates='orders', lazy='selectin'
    )
    order_fireworks: Mapped[List['OrderFirework']] = relationship(
        lazy='selectin'
    )
    status: Mapped['OrderStatus'] = relationship(lazy='selectin')


class OrderFirework(BaseJFModel):
    id: Mapped[int_pk]
    order_id: Mapped[int] = mapped_column(
        ForeignKey('order.id', ondelete='CASCADE'), nullable=False
    )
    firework_id: Mapped[int] = mapped_column(
        ForeignKey('firework.id', ondelete='SET NULL'), nullable=True
    )
    amount: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(
            FIREWORK_PRICE_NUMBER_OF_DIGITS, FIREWORK_PRICE_FRACTIONAL_PART
        ),
        nullable=False,
    )

    order: Mapped['Order'] = relationship(back_populates='order_fireworks')
    firework: Mapped['Firework'] = relationship(
        back_populates='order_fireworks', lazy='selectin'
    )
