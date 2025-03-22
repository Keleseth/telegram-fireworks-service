from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import int_pk
from src.models.base import BaseJFModel

if TYPE_CHECKING:
    from src.models.product import Firework


class FireworkProperty(BaseJFModel):
    """Модель для хранения описаний характеристик фейерверков.

    Поля:
        1. id: уникальный идентификатор.
        2. property_description: описания характеристик фейерверка.
        3. firework_id: id фейерверка, к которому относится характеристика.
        4. firework: связь с моделью Firework.
    """

    __tablename__ = 'firework_property'

    id: Mapped[int_pk]
    property_description: Mapped[str] = mapped_column(nullable=False)
    firework_id: Mapped[int] = mapped_column(ForeignKey('firework.id'))

    firework: Mapped['Firework'] = relationship(
        'Firework', back_populates='properties'
    )
