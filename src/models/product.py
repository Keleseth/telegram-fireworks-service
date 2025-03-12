from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import int_pk, str_not_null_and_unique
from src.models.base import BaseJFModel

if TYPE_CHECKING:
    from src.database.alembic_models import (
        FavoriteFirework,
        FireworkDiscount,
        Media,
        OrderFirework,
    )

FIREWORK_PRICE_NUMBER_OF_DIGITS = 10
FIREWORK_PRICE_FRACTIONAL_PART = 2


class FireworkTag(BaseJFModel):
    """Промежуточная модель many-to-many.

    Поля:
        1. id: уникальный индетификатор.
        2. tag_id: id тега.
        3. firework_id: id товара.

    Связывает между собой модели Tag и Firework.
    """

    __tablename__ = 'firework_tag'

    id: Mapped[int_pk]
    tag_id: Mapped[int] = mapped_column(ForeignKey('tag.id'))
    firework_id: Mapped[int] = mapped_column(ForeignKey('firework.id'))


class Tag(BaseJFModel):
    """Модель тегов.

    Поля:
        1. id: уникальный индетификатор.
        2. name: уникальное название тега (обязательное поле).
        3. fireworks: объекты модели Firework с текущим тегом.

    """

    id: Mapped[int_pk]
    name: Mapped[str_not_null_and_unique]
    fireworks: Mapped[list['Firework']] = relationship(
        'Firework',
        secondary='firework_tag',
        back_populates='tags',
        lazy='joined',
    )


class Category(BaseJFModel):
    """Модель категорий.

    Поля:
        1. id: уникальный индетификатор.
        2. name: уникальное название категории (обязательное поле).
        3. parent_category_id: id родительской категории (опционально).
        4. categories: все подкатегории текущей категории.
        5. parent_category: родительская категория.
        6. fireworks: все товары с текущей категорией.
    """

    id: Mapped[int_pk]
    name: Mapped[str_not_null_and_unique]
    parent_category_id: Mapped[int] = mapped_column(ForeignKey('category.id'))
    categories: Mapped[list['Category']] = relationship(
        'Category',
        back_populates='parent_category',
        cascade='all, delete-orphan',
    )
    parent_category: Mapped['Category'] = relationship(
        'Category', back_populates='categories', remote_side=[id]
    )
    fireworks: Mapped[list['Firework']] = relationship(
        'Firework', back_populates='category', lazy='joined'
    )


class Firework(BaseJFModel):
    """Модель товара.

    Поля:
        1. id: уникальный индетификатор.
        2. name: уникальное название товара (обязательное поле).
        3. description: описание товара (опционально).
        4. price: цена за единицу товара (опционально).
        5. category_id: id категории, к которой принадлежит товар
            (обязательное поле).
        6. category: категория товара.
        7. tags: теги, относящиеся к товару (опционально).
        8. external_id: артикул (обязательное поле).
        9. media: медиа-файлы, связанные с товаром.
        10. article: артикул товара.
    """

    id: Mapped[int_pk]
    name: Mapped[str_not_null_and_unique]
    description: Mapped[str | None]
    price: Mapped[Numeric] = mapped_column(
        Numeric(
            FIREWORK_PRICE_NUMBER_OF_DIGITS, FIREWORK_PRICE_FRACTIONAL_PART
        )
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey('category.id'), nullable=True
    )
    category: Mapped['Category'] = relationship(
        'Category', back_populates='fireworks'
    )
    tags: Mapped[list['Tag']] = relationship(
        'Tag',
        secondary='firework_tag',
        back_populates='fireworks',
        lazy='joined',
    )
    media: Mapped[list['Media']] = relationship(
        'Media',
        secondary='firework_media',
        back_populates='fireworks',
        lazy='joined',
    )
    order_fireworks: Mapped[list['OrderFirework']] = relationship(
        back_populates='firework'
    )
    favorited_by_users: Mapped[list['FavoriteFirework']] = relationship(
        back_populates='firework'
    )
    discounts: Mapped[list['FireworkDiscount']] = relationship(
        back_populates='firework'
    )
    image_url: Mapped[str | None]
    video_url: Mapped[str | None]
    external_id: Mapped[str] = mapped_column(nullable=False)
    article: Mapped[str] = mapped_column(nullable=False)
