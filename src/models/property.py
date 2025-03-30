from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import int_pk
from src.models.base import BaseJFModel

if TYPE_CHECKING:
    from src.models.product import Firework


class PropertyField(BaseJFModel):
    """Модель для хранения имен дополнительных полей характеристик.

    Поля:
        1. id: уникальный идентификатор.
        2. field_name: название поля характеристики.
    """

    __tablename__ = 'property_field'

    id: Mapped[int_pk]
    field_name: Mapped[str] = mapped_column(unique=True, nullable=False)

    def __repr__(self) -> str:
        return self.field_name


class FireworkProperty(BaseJFModel):
    """Модель для хранения характеристик фейерверков.

    Поля:
        1. id: уникальный идентификатор.
        2. field_id: id поля характеристики.
        3. value: значение характеристики.
        4. firework_id: id фейерверка.
        5. firework: связь с моделью Firework.
        6. field: связь с моделью PropertyField.
    """

    __tablename__ = 'firework_property'

    id: Mapped[int_pk]
    field_id: Mapped[int] = mapped_column(ForeignKey('property_field.id'))
    value: Mapped[str] = mapped_column(nullable=False)
    firework_id: Mapped[int] = mapped_column(ForeignKey('firework.id'))

    firework: Mapped['Firework'] = relationship(
        'Firework', back_populates='properties'
    )
    field: Mapped['PropertyField'] = relationship('PropertyField')

    def __repr__(self) -> str:
        return self.value
