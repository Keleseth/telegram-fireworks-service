from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Numeric
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
    2. status_text: Текст, представляющий состояние, в котором находится заказ.
    """

    id: Mapped[int_pk]
    status_text: Mapped[str]


class Order(BaseJFModel):
    """Модель заказов.

    Поля:
    1. id: int - Уникальный идентификатор заказа (primary key).
    2. user_id: UUID - Ссылка на пользователя, оформившего заказ
    (внешний ключ к таблице user).
    3. status_id: int - Текущее состояние заказа
    (внешний ключ к таблице orderstatus).
    4. user_address_id: int | None - Ссылка на конкретный адрес пользователя
    из таблицы useraddress (может быть null).
    5. user: User - Связь с моделью User (многие-к-одному),
    подтягивается автоматически с помощью lazy='selectin'.
    6. user_address: UserAddress | None - Связь с моделью UserAddress
    (многие-к-одному), может быть null, lazy='selectin'.
    7. order_fireworks: List[OrderFirework] - Список товаров в заказе
    (один-ко-многим), подтягивается с lazy='selectin'.
    8. status: OrderStatus - Связь с моделью OrderStatus
    (многие-к-одному), подтягивается с lazy='selectin'.
    """

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
    """Таблица содержащая перечень товаров заказа, их количество и цену.

    Поля:
    1. id: int - primary key.
    2. order_id: Ссылка на заказ (внешний ключ к таблице order).
    3. firework_id: Ссылка на товар
    (внешний ключ к таблице firework, может быть null).
    4. amount: Количество единиц товара в заказе.
    5. price_per_unit: Цена за единицу товара (точное десятичное значение).
    """

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
