from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, condecimal, conint

from src.schemas.user import TelegramIDSchema


class BaseOrderSchema(BaseModel):
    pass


class FireworkSchema(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)


class OrderFireworkSchema(BaseModel):
    firework: FireworkSchema
    amount: conint(gt=0)
    price_per_unit: condecimal(max_digits=10, decimal_places=2)
    model_config = ConfigDict(from_attributes=True)


class ReadOrderSchema(BaseModel):
    id: int
    status: str
    user_address_id: Optional[int]
    fio: Optional[str]
    phone: Optional[str]
    operator_call: bool
    total: Optional[condecimal(max_digits=10, decimal_places=2)]
    order_fireworks: List[OrderFireworkSchema]
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)


class UpdateOrderAddressSchema(BaseOrderSchema):
    user_address_id: Optional[int]
    fio: Optional[str]
    phone: Optional[str]
    operator_call: bool


class OrderAddressUpdateRequest(BaseModel):
    # Новая схема для PATCH /orders/{order_id}/address
    telegram_schema: TelegramIDSchema
    data: UpdateOrderAddressSchema


class UpdateOrderStatusSchema(BaseOrderSchema):
    status_id: int


class DeleteOrderSchema(BaseOrderSchema):
    order_id: int
