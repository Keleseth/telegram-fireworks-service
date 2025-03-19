from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import int_pk, str_not_null_and_unique
from src.models.base import BaseJFModel

if TYPE_CHECKING:
    from src.models.cart import Cart
    from src.models.discounts import Discount
    from src.models.favorite import FavoriteFirework
    from src.models.media import FireworkMedia
    from src.models.order import OrderFirework


FIREWORK_PRICE_NUMBER_OF_DIGITS = 10
FIREWORK_PRICE_FRACTIONAL_PART = 2
print('>>> Загрузка Firework')


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
        lazy='selectin',
    )


class Category(BaseJFModel):
    """Модель категорий.

    Поля:
        1. id: уникальный индетификатор.
        2. name: уникальное название категории (обязательное поле).
        3. parent_category_id: id родительской категории (опционально).
        4. categories: все подкатегории текущей категории.
        5. parent_category: родительская категория.
        6. fireworks: все товары категории.
    """

    id: Mapped[int] = mapped_column('id', primary_key=True)
    name: Mapped[str_not_null_and_unique]
    parent_category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('category.id'), nullable=True
    )
    categories: Mapped[list['Category']] = relationship(
        'Category',
        back_populates='parent_category',
        cascade='all, delete-orphan',
    )
    parent_category: Mapped[Optional['Category']] = relationship(
        'Category', back_populates='categories', remote_side=[id]
    )
    fireworks: Mapped[list['Firework']] = relationship(
        'Firework', back_populates='category', lazy='selectin'
    )


class Firework(BaseJFModel):
    """Модель товара.

    Поля:
        1. id: уникальный индетификатор.
        2. code: код товара (обязательное поле).
        3. name: уникальное название товара (обязательное поле).
        4. measurement_unit: единица измерения.
        5. description: описание товара (опционально).
        6. price: цена за единицу товара (опционально).
        7. category_id: id категории, к которой принадлежит товар
            (обязательное поле).
        8. category: категория товара.
        9. tags: теги, относящиеся к товару (опционально).
        10. media: media-файлы (опционально).
        11. charges_count: количество зарядов (опционально).
        12. effects_count: количество эффектов (опционально).
        13. product_size: размер продукта (обязательное поле).
        14. packing_material: материал упаковки (опционально).
        15. article: артикул товара (обязательное поле).
    """

    id: Mapped[int_pk]
    code: Mapped[str_not_null_and_unique]
    name: Mapped[str_not_null_and_unique]
    measurement_unit: Mapped[str] = mapped_column(nullable=False)
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
        'Category', back_populates='fireworks', lazy='joined'
    )
    tags: Mapped[list['Tag']] = relationship(
        'Tag',
        secondary='firework_tag',
        back_populates='fireworks',
        lazy='joined',
    )
    media: Mapped[list['FireworkMedia']] = relationship(
        'FireworkMedia',
        back_populates='fireworks',
        lazy='joined',
        cascade='all, delete',
    )
    charges_count: Mapped[int | None]
    effects_count: Mapped[int | None]
    product_size: Mapped[str] = mapped_column(nullable=False)
    packing_material: Mapped[str | None]
    order_fireworks: Mapped[list['OrderFirework']] = relationship(
        back_populates='firework'
    )
    favorited_by_users: Mapped[list['FavoriteFirework']] = relationship(
        back_populates='firework'
    )
    discounts: Mapped[list['Discount']] = relationship(
        secondary='fireworkdiscount',
        lazy='joined',
        back_populates='fireworks',
    )
    carts: Mapped[List['Cart']] = relationship(
        back_populates='firework', cascade='all, delete-orphan'
    )
    article: Mapped[str] = mapped_column(nullable=False)
