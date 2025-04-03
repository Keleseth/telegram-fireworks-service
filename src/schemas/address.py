from pydantic import BaseModel, Field

MAX_LENGTH = 255


class BaseAddressSchema(BaseModel):
    """Базовая схема адресов."""

    address: str = Field(..., max_length=MAX_LENGTH)


class CreateAddressSchema(BaseAddressSchema):
    """Схема для создания адреса."""

    telegram_id: int


class ReadAddressSchema(BaseAddressSchema):
    """Схема для чтения адреса."""

    id: int


class UpdateAddressSchema(BaseAddressSchema):
    """Схема для обновления адреса."""

    telegram_id: int


class DeleteAddressSchema(BaseModel):
    """Схема для удаления адреса."""

    telegram_id: int


class UserAddressResponseSchema(BaseModel):
    user_address_id: int
    address: str
