from pydantic import BaseModel

# TODO: telegram_id будет в теле запроса
# Схема на удаление, создание, изменение объекта должна содержать telegram_id.


class BaseCartSchema(BaseModel):
    """Базовая схема корзины."""


class ReadCartSchema(BaseModel):
    """Докстринг."""


class CreateCartSchema(BaseModel):
    """Докстринг."""


class UpdateCartSchema(BaseModel):
    """Докстринг."""


class DeleteCartSchema(BaseModel):
    """Докстринг."""
