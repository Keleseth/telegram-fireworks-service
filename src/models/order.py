from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseJFModel


class OrderStatus(Enum):
    CREATED = 'created'
    PAID = 'paid'
    PENDING = 'pending'


class Order(BaseJFModel):
    """Модель для заказов."""

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('user.id'), nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name='order_status'), nullable=False
    )
    user_address_id: Mapped[int] = mapped_column(
        ForeignKey('useraddress.id'), nullable=False
    )

    user = relationship('User', back_populates='orders')
    user_address = relationship('UserAddress', back_populates='orders')
    fireworks = relationship('OrderFirework', back_populates='order')


class OrderFirework(BaseJFModel):
    """Связывающая модель для заказов и товара."""

    firework_id: Mapped[int] = mapped_column(
        ForeignKey('firework.id'), nullable=False
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey('order.id'), nullable=False
    )
    price_per_unit: Mapped[Numeric] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    amount: Mapped[int] = mapped_column(nullable=False, default=1)

    firework = relationship('Firework', back_populates='orders')
    order = relationship('Order', back_populates='fireworks')
