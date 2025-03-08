from typing import ClassVar

from sqlalchemy import String, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseJFModel, unique_str_annotate


FIREWORK_PRICE_NUMBER_OF_DIGITS = 10
FIREWORK_PRICE_FRACTIONAL_PART = 2


class FireworkTag(BaseJFModel):
    """Промежуточная модель many-to-many.
    Связывает между собой модели Tag и Firework.

    Поля:
        tag_id: id тега.
        firework_id: id товара.
    """

    __tablename__ = 'firework_tag'

    tag_id: Mapped[int] = mapped_column(
        ForeignKey('tag.id')
    )
    firework_id: Mapped[int] = mapped_column(
        ForeignKey('firework.id')
    )


class Tag(BaseJFModel):
    """Модель тегов.

    Поля:
        name: уникальное название тега (обязательное поле).
        fireworks: объекты модели Firework с текущим тегом.
    
    """
    __tablename__ = 'tag'

    name: Mapped[str] = mapped_column(unique=True)
    fireworks: Mapped[list['Firework']] = relationship(
        'Firework',
        secondary='firework_tag',
        back_populates='tags',
        lazy='joined'
    )


class Category(BaseJFModel):
    """Модель категорий.

    Поля:
        name: уникальное название категории (обязательное поле).
        parent_category_id: id родительской категории (опционально).
        categories: все подкатегории текущей категории.
        fireworks: все товары с текущей категорией.
    """

    __tablename__ = 'category'

    name: Mapped[str] = mapped_column(unique=True)
    parent_category_id: Mapped[int] = mapped_column(
        ForeignKey('category.id'),
        nullable=True,
        
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
        name: уникальное название товара (обязательное поле).
        description: описание товара (опционально).
        price: цена за единицу товара (опционально).
        category_id: id категории, к которой принадлежит товар
            (обязательное поле).
        category: категория товара.
        tags: теги, относящиеся к товару (опционально).
        image_url: ссылки на изображения (опционально).
        video_url: ссылки на видео (опционально).
        external_id: артикул  (обязательное поле).
    """
    __tablename__ = 'firework'

    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    price: Mapped[Numeric] = mapped_column(
        Numeric(
            FIREWORK_PRICE_NUMBER_OF_DIGITS,
            FIREWORK_PRICE_FRACTIONAL_PART
        ),
        nullable=True
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
    image_url: Mapped[str | None]
    video_url: Mapped[str | None]
    external_id: Mapped[str]
