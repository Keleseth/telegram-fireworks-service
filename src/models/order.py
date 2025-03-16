from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import Float, ForeignKey, Integer
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
    """Таблица с текстом статусов для заказов.

    Поля:
    1. id: int - primary key.
    2. status_ttext: Текст представляющий состояние в котором находится заказ.
    """

    id: Mapped[int_pk]
    status_text: Mapped[str]


class Order(BaseJFModel):
    """Модель заказов.

    Поля:
    1. id: int - primary key.
    2. user_id: ссылка на пользователя.
    3. status_id: Текущее состояние заказа.
    4. user_address_id: ссылка на конкретный адрес пользователя,
    их может быть несколько.
    """

    id: Mapped[int_pk]
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('user.id'), nullable=False
    )
    status_id: Mapped['OrderStatus'] = mapped_column(
        ForeignKey('orderstatus.id'), nullable=False
    )
    user_address_id: Mapped[UUID | None] = mapped_column(
        ForeignKey('useraddress.id', ondelete='SET NULL'), nullable=True
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
    """Таблица содержащая перечень товаров заказа, их кол-во и цену.

    Поля:
    1. id: int - primary key.
    2. order_id: ссылка заказ.
    3. firework_id ссылка товар.
    4. amount: количество товара.
    5. цена за единицу товара.
    """

    id: Mapped[int_pk]
    order_id: Mapped[int] = mapped_column(
        ForeignKey('order.id', ondelete='CASCADE'), nullable=False
    )
    firework_id: Mapped[int] = mapped_column(
        ForeignKey('firework.id', ondelete='SET NULL'), nullable=True
    )
    amount: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    price_per_unit: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    order: Mapped['Order'] = relationship(back_populates='order_fireworks')
    firework: Mapped['Firework'] = relationship(
        back_populates='order_fireworks'
    )
