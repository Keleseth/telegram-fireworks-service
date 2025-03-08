from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import BaseJFModel
from src.database.annotations import int_pk, not_null_and_unique

FIREWORK_PRICE_NUMBER_OF_DIGITS = 10
FIREWORK_PRICE_FRACTIONAL_PART = 2


class FireworkTag(BaseJFModel):
    """Промежуточная модель many-to-many.

    Поля:
        id: уникальный индетификатор.
        tag_id: id тега.
        firework_id: id товара.

    Связывает между собой модели Tag и Firework.
    """

    __tablename__ = 'firework_tag'

    id: Mapped[int_pk]
    tag_id: Mapped[int] = mapped_column(
        ForeignKey('tag.id')
    )
    firework_id: Mapped[int] = mapped_column(
        ForeignKey('firework.id')
    )


class Tag(BaseJFModel):
    """Модель тегов.

    Поля:
        id: уникальный индетификатор.
        name: уникальное название тега (обязательное поле).
        fireworks: объекты модели Firework с текущим тегом.

    """

    id: Mapped[int_pk]
    name: Mapped[not_null_and_unique]
    fireworks: Mapped[list['Firework']] = relationship(
        'Firework',
        secondary='firework_tag',
        back_populates='tags',
        lazy='joined'
    )


class Category(BaseJFModel):
    """Модель категорий.

    Поля:
        id: уникальный индетификатор.
        name: уникальное название категории (обязательное поле).
        parent_category_id: id родительской категории (опционально).
        categories: все подкатегории текущей категории.
        fireworks: все товары с текущей категорией.
    """

    id: Mapped[int_pk]
    name: Mapped[not_null_and_unique]
    parent_category_id: Mapped[int] = mapped_column(
        ForeignKey('category.id')
    )
    categories: Mapped[list['Category']] = relationship(
        'Category',
        back_populates='parent_category',
        cascade='all, delete-orphan'
    )
    parent_category: Mapped['Category'] = relationship(
        'Category',
        back_populates='categories',
        remote_side=[id]
    )
    fireworks: Mapped[list['Firework']] = relationship(
        'Firework',
        back_populates='category',
        lazy='joined'
    )


class Firework(BaseJFModel):
    """Модель товара.

    Поля:
        id: уникальный индетификатор.
        name: уникальное название товара (обязательное поле).
        description: описание товара (опционально).
        price: цена за единицу товара (опционально).
        category_id: id категории, к которой принадлежит товар
            (обязательное поле).
        category: категория товара.
        tags: теги, относящиеся к товару (опционально).
        image_url: ссылки на изображения (опционально).
        video_url: ссылки на видео (опционально).
        external_id: артикул (обязательное поле).
        media: медиа-файлы, связанные с товаром.
    """

    id: Mapped[int_pk]
    name: Mapped[not_null_and_unique]
    description: Mapped[str | None]
    price: Mapped[Numeric] = mapped_column(
        Numeric(
            FIREWORK_PRICE_NUMBER_OF_DIGITS,
            FIREWORK_PRICE_FRACTIONAL_PART
        )
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey('category.id'),
        nullable=True
    )
    category: Mapped['Category'] = relationship(
        'Category',
        back_populates='fireworks'
    )
    tags: Mapped[list['Tag']] = relationship(
        'Tag',
        secondary='firework_tag',
        back_populates='fireworks',
        lazy='joined'
    )
    media: Mapped[list['Media']] = relationship(
        'Media',
        secondary='firework_media',
        back_populates='fireworks',
        lazy='joined'
    )
    image_url: Mapped[str | None]
    video_url: Mapped[str | None]
    external_id: Mapped[str] = mapped_column(nullable=False)
