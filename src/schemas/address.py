from pydantic import BaseModel

# TODO: telegram_id будет в теле запроса
# Схема на удаление, создание, изменение объекта должна содержать telegram_id.


class BaseAddressSchema(BaseModel):
    """Базовая схема адресов."""


class ReadAddressSchema(BaseModel):
    """Докстринг."""


class CreateAddressSchema(BaseModel):
    """Докстринг."""


class UpdateAddressSchema(BaseModel):
    """Докстринг."""


class DeleteAddressSchema(BaseModel):
    """Докстринг."""
