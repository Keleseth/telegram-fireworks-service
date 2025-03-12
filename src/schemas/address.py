from pydantic import BaseModel, Field

MAX_LENGTH = 255


class BaseAddressSchema(BaseModel):
    """Базовая схема адресов."""

    adress: str = Field(..., max_length=MAX_LENGTH)


class ReadAddressSchema(BaseModel):
    """Докстринг."""

    telegram_id: int


class CreateAddressSchema(BaseAddressSchema):
    """Докстринг."""

    telegram_id: int


class UpdateAddressSchema(BaseAddressSchema):
    """Докстринг."""

    telegram_id: int


class DeleteAddressSchema(BaseAddressSchema):
    """Докстринг."""

    telegram_id: int
