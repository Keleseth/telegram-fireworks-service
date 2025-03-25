from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Numeric, func, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import int_pk, str_not_null_and_unique
from src.models.base import BaseJFModel
from src.models.favorite import FavoriteFirework

if TYPE_CHECKING:
    from src.models.cart import Cart
    from src.models.discounts import Discount
    from src.models.favorite import FavoriteFirework
    from src.models.media import Media
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

    def __repr__(self) -> str:
        """Метод представляющий объект."""
        return self.name


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

    def __repr__(self) -> str:
        """Метод представляющий объект."""
        return self.name


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
    price: Mapped[Decimal] = mapped_column(
        Numeric(
            FIREWORK_PRICE_NUMBER_OF_DIGITS, FIREWORK_PRICE_FRACTIONAL_PART
        )
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey('category.id'), nullable=True
    )
    category: Mapped['Category'] = relationship(
        'Category', back_populates='fireworks', lazy='selectin'
    )
    tags: Mapped[list['Tag']] = relationship(
        'Tag',
        secondary='firework_tag',
        back_populates='fireworks',
        lazy='selectin',
    )
    media: Mapped[list['Media']] = relationship(
        'Media',
        back_populates='fireworks',
        lazy='selectin',
        secondary='firework_media',
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
        lazy='selectin',
        back_populates='fireworks',
    )
    carts: Mapped[List['Cart']] = relationship(
        back_populates='firework', cascade='all, delete-orphan'
    )
    article: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return self.name

    # --- админская часть ---

    @hybrid_property
    def favorited_count(self):
        # это питоновская часть, которая вызывается у конкретного объекта
        # когда мы делаем firework.favorited_count
        return len(self.favorited_by_users)

    @favorited_count.expression
    def favorited_count(self):
        return (
            select(func.count(FavoriteFirework.id))
            .where(FavoriteFirework.firework_id == self.id)
            .correlate(self)
            .scalar_subquery()
        )

    @hybrid_property
    def ordered_count(self) -> int:
        user_ids = [
            ofw.order.user_id
            for ofw in self.order_fireworks
            if ofw.order is not None
        ]
        return len(user_ids)

    @ordered_count.expression
    def ordered_count(self):
        from src.models.order import Order, OrderFirework

        return (
            select(func.count(func.distinct(Order.user_id)))
            .select_from(OrderFirework)
            .join(Order, Order.id == OrderFirework.order_id)
            .where(OrderFirework.firework_id == self.id)
            .scalar_subquery()
        )
