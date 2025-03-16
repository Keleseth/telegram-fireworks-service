from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, condecimal, conint


class BaseOrderSchema(BaseModel):
    """Базовая схема заказов."""

    pass


class OrderFireworkSchema(BaseModel):
    firework_id: int
    amount: conint(gt=0)
    price_per_unit: condecimal(max_digits=10, decimal_places=2)
    model_config = ConfigDict(from_attributes=True)


class ReadOrderSchema(BaseModel):
    id: int
    status: str
    user_address_id: Optional[UUID]
    order_fireworks: List[OrderFireworkSchema]
    user_id: UUID


class UpdateOrderAddressSchema(BaseOrderSchema):
    user_address_id: UUID


class UpdateOrderStatusSchema(BaseOrderSchema):
    status_id: int


class DeleteOrderSchema(BaseOrderSchema):
    order_id: int
