from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import BaseJFModel
from src.database.annotations import int_pk

if TYPE_CHECKING:
    from src.models.product import Firework


class FireworkMedia(BaseJFModel):
    """Промежуточная модель many-to-many.

    Поля:
        id: уникальный индетификатор.
        firework_id: id товара.
        image_id: id медиа.

    Связывает между собой модели Media и Firework.
    """

    __tablename__ = 'firework_media'

    id: Mapped[int_pk]
    firework_id: Mapped[int] = mapped_column(ForeignKey('firework.id'))
    image_id: Mapped[int] = mapped_column(ForeignKey('media.id'))


class Media(BaseJFModel):
    """Модель для хранения медиа-файлов.

    Поля:
        id: уникальный индетификатор.
        media_url: ссылка на медиа-файл.
        media_type: тип медиа-файла.
        fireworks: товары, относящиеся к медиа-файлу.
    """

    id: Mapped[int_pk]
    media_url: Mapped[str] = mapped_column(unique=True, nullable=False)
    media_type: Mapped[str] = mapped_column(nullable=False)
    fireworks: Mapped[list['Firework']] = relationship(
        'Firework',
        secondary='firework_media',
        back_populates='media',
        lazy='joined',
        cascade='all, delete',
    )
