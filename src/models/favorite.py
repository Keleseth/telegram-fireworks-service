from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.alembic_models import BaseJFModel
from src.database.annotations import int_pk

if TYPE_CHECKING:
    from src.database.alembic_models import Firework, User


class FavoriteFirework(BaseJFModel):
    """Таблица связи пользователей и избранных товаров."""

    id: Mapped[int_pk]
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    firework_id: Mapped[int] = mapped_column(
        ForeignKey('firework.id', ondelete='CASCADE'), nullable=False
    )

    user: Mapped['User'] = relationship(back_populates='favorite_fireworks')
    firework: Mapped['Firework'] = relationship(
        back_populates='favorited_by_users'
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'firework_id', name='unique_favorite'),
    )
