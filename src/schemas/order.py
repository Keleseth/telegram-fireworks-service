from pydantic import BaseModel

# TODO: telegram_id будет в теле запроса
# Схема на удаление, создание, изменение объекта должна содержать telegram_id.


class BaseOrderSchema(BaseModel):
    """Базовая схема заказов."""


class ReadOrderSchema(BaseModel):
    """Докстринг."""


class CreateOrderSchema(BaseModel):
    """Докстринг."""


class UpdateOrderSchema(BaseModel):
    """Докстринг."""


class DeleteOrderSchema(BaseModel):
    """Докстринг."""
