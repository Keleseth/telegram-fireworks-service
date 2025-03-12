from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, condecimal, conint

# TODO: telegram_id будет в теле запроса
# Схема на удаление, создание, изменение объекта должна содержать telegram_id.


class BaseOrderSchema(BaseModel):
    """Базовая схема заказов, включающая Telegram ID."""

    telegram_id: int


class OrderFireworkSchema(BaseModel):
    """Схема для товаров в заказе."""

    firework_id: int
    amount: conint(gt=0)
    price_per_unit: condecimal(max_digits=10, decimal_places=2)


class ReadOrderSchema(BaseModel):
    """Схема для просмотра заказа."""

    id: int
    status: str
    user_address_id: Optional[int]
    order_fireworks: List[OrderFireworkSchema]
    user_id: UUID


class CreateOrderSchema(BaseOrderSchema):
    """Схема для создания заказа."""

    user_address_id: Optional[int]
    order_fireworks: List[OrderFireworkSchema]


class UpdateOrderSchema(BaseOrderSchema):
    """Схема для обновления заказа.

    (Разрешено только изменение товаров и адреса).
    """

    order_id: int
    user_address_id: Optional[int]
    order_fireworks: Optional[List[OrderFireworkSchema]]


class DeleteOrderSchema(BaseOrderSchema):
    """Схема для удаления заказа."""

    order_id: int
