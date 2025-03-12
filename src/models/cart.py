from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database.alembic_models import BaseJFModel
from src.database.annotations import int_pk
from src.models.product import Firework
from src.models.user import User

# if TYPE_CHECKING:
#     from src.models.product import Firework
#     from src.models.user import User


class Cart(BaseJFModel):
    """Модель корзины пользователя.

    Поля:
    id: int - primary key.
    firework_id: Ссылка на таблицу Firework.
    user_id: Ссылка на таблицу User.
    amount: Количество единиц конкретного товара в корзине пользователя.
    """

    id: Mapped[int_pk]
    firework_id: Mapped['Firework'] = mapped_column(
        ForeignKey('firework.id'),
        nullable=False,
    )
    user_id: Mapped['User'] = mapped_column(
        ForeignKey('user.id'), nullable=False
    )
    amount: Mapped[int] = mapped_column(nullable=False, default=1)

    __table_args__ = (
        CheckConstraint('amount >= 1', name='min_cart_amount'),
        UniqueConstraint('user_id', 'firework_id', name='unique_cart_item'),
    )
