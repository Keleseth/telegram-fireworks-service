from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, condecimal, conint


class BaseOrderSchema(BaseModel):
    """Базовая схема заказов, включающая Telegram ID."""

    telegram_id: int


class OrderFireworkSchema(BaseModel):
    """Схема для товаров в заказе."""

    firework_id: int
    amount: conint(gt=0)
    price_per_unit: condecimal(max_digits=10, decimal_places=2)

    model_config = ConfigDict(from_attributes=True)


class ReadOrderSchema(BaseModel):
    """Схема для просмотра заказа."""

    id: int
    status: str
    user_address_id: Optional[int]
    order_fireworks: List[OrderFireworkSchema]
    user_id: UUID


class CreateOrderSchema(BaseOrderSchema):
    """Схема для создания заказа."""

    user_address_id: Optional[int] = None
    order_fireworks: List[OrderFireworkSchema]


class UpdateOrderAddressSchema(BaseOrderSchema):
    """Схема для обновления адреса заказа."""

    user_address_id: int


class UpdateOrderStatusSchema(BaseOrderSchema):
    """Схема для изменения статуса заказа."""

    status_id: int  # Передаём ID статуса из OrderStatus


class DeleteOrderSchema(BaseOrderSchema):
    """Схема для удаления заказа."""

    order_id: int
