
from collections import Counter
from datetime import date
from typing import TYPE_CHECKING, List

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import BigInteger, Boolean, Date, func, select, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseJFModel
from src.models.order import Order

if TYPE_CHECKING:
    from src.models.address import UserAddress
    from src.models.cart import Cart
    from src.models.favorite import FavoriteFirework
    from src.models.order import Order


# class PreferedLanguage(str, PyEnum):  # TODO оставляем на реализацию
#     EN = 'english'
#     RU = 'русский'


class User(BaseJFModel, SQLAlchemyBaseUserTableUUID):  # type: ignore[misc]
    """Основная модель пользователя.

    Поля:
        id: UUID айди.
        telegram_id: айди в телеграмме.
        email: почта пользователя.
        age_verified: является ли пользователь совершеннолетним (18+).
        name: имя в телеграмме пользователя.
        nickname: ник в телеграмме пользователя.
        phone_number: телефон пользователя.
        prefered_language: предпочитаемый язык.
        is_admin: является ли пользователь админом.
        is_superuser: является ли пользователь суперадмином.
    """

    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger, unique=True, nullable=False
    )
    email: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True
    )  # type: ignore
    hashed_password: Mapped[str | None] = mapped_column(String, nullable=True)  # type: ignore
    name: Mapped[str] = mapped_column(String, nullable=False)
    nickname: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True
    )
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True
    )
    age_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    # prefered_language: Mapped[PreferedLanguage] = mapped_column(
    #     Enum(PreferedLanguage), default=PreferedLanguage.RU
    # )  # TODO оставляем на реализацию
    favorite_fireworks: Mapped[List['FavoriteFirework']] = relationship(
        back_populates='user'
    )
    cart: Mapped[List['Cart']] = relationship(cascade='all, delete-orphan')
    orders: Mapped[List['Order']] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    addresses: Mapped[List['UserAddress']] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )  # type: ignore

    __table_args__ = {'extend_existing': True}

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(id={self.id!r}, name={self.name!r}, '
        )

    # --- админская часть ---

    @hybrid_property
    def has_orders(self) -> int:
        return len(self.orders)

    @has_orders.expression
    def has_orders(self):
        """Возвращает кол-во заказов пользователя со статусом `paid`."""
        return (
            select(func.count(Order.id) > 0)
            .where(Order.user_id == self.id)
            .where(Order.status.has(status_text='paid'))
            .correlate(self)
            .scalar_subquery()
        )

    @property
    def top_2_categories(self):
        """Возвращает 2 любимы категории пользователя(судя по заказам)."""
        category_names = []
        for order in self.orders:
            for item in order.order_fireworks:  # или order.order_items
                if item.firework and item.firework.category:
                    category_names.append(item.firework.category.name)

        # Считаем в Counter и берем топ-2
        counter = Counter(category_names)
        top_two = [name for name, _ in counter.most_common(2)]
        return top_two if top_two else None
