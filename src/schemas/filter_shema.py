# Файл для создания схем забирающих из тела запроса переданыне фильтры.

from typing import List, Optional

from pydantic import BaseModel, Field


class FireworkFilterSchema(BaseModel):
    """Схема для фильтрации фейеверков."""

    name: Optional[str] = Field(
        default=None, title='Фильтр по совпадению с именем фейеверка.'
    )
    number_of_volleys: Optional[int] = Field(
        default=None, title='Фильтр по количеству залпов.'
    )
    categories: Optional[List[str]] = Field(
        default=None, title='Фильтр по категориям.'
    )
    # sub_categories: Optional[List[str]] = Field(
    #     None, title='Фильтр по подкатегориям.'
    # )
    article: Optional[str] = Field(default=None, title='Фильтр по артикулу')
    tags: Optional[List[str]] = Field(
        default=None, title='Список фильтров по тегам.'
    )
    min_price: Optional[int] = Field(default=None, title='Минимальная цена.')
    max_price: Optional[int] = Field(default=None, title='Максимальная цена.')
    order_by: Optional[List[str]] = Field(
        ['name'], title='Сортировка по полям.'
    )

    model_config = {
        'extra': 'ignore',
    }
