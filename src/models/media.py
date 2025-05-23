from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import int_pk, str_not_null_and_unique
from src.models.base import BaseJFModel

if TYPE_CHECKING:
    from src.models.product import Firework


class FireworkMedia(BaseJFModel):
    """Промежуточная модель many-to-many.

    Поля:
        1. firework_id: id товара.
        2. image_id: id медиа.

    Связывает между собой модели Media и Firework.
    """

    __tablename__ = 'firework_media'

    firework_id: Mapped[int] = mapped_column(
        ForeignKey('firework.id'), primary_key=True
    )
    image_id: Mapped[int] = mapped_column(
        ForeignKey('media.id'), primary_key=True
    )

    def __repr__(self) -> str:
        return f'{self.firework_id}:{self.image_id}'


class Media(BaseJFModel):
    """Модель для хранения медиа-файлов.

    Поля:
        1. id: уникальный индетификатор.
        2. media_url: ссылка на медиа-файл.
        3. media_type: тип медиа-файла.
        4. fireworks: товары, относящиеся к медиа-файлу.
    """

    id: Mapped[int_pk]
    media_url: Mapped[str_not_null_and_unique]
    media_type: Mapped[str] = mapped_column(nullable=False)
    fireworks: Mapped[list['Firework']] = relationship(
        'Firework',
        back_populates='media',
        secondary='firework_media',
        lazy='selectin',
        cascade='all, delete',
    )
    formatted_media: Mapped[list['FormattedMedia']] = relationship(
        'FormattedMedia',
        back_populates='media',
        lazy='selectin',
        cascade='all, delete',
    )

    def __repr__(self) -> str:
        return self.media_url


class FormattedMedia(BaseJFModel):
    id: Mapped[int_pk]
    file: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    media_id: Mapped[int] = mapped_column(
        ForeignKey('media.id'), primary_key=True
    )
    media: Mapped[Media] = relationship(
        'Media', back_populates='formatted_media', lazy='selectin'
    )

    def __repr__(self) -> str:
        return f'{self.id}: {self.type}'
