from pydantic import BaseModel

# TODO: telegram_id будет в теле запроса
# Схема на удаление, создание, изменение объекта должна содержать telegram_id.


class MessageResponse(BaseModel):
    """Базовая схема для ответов."""

    message: str


class BaseCartSchema(BaseModel):
    """Базовая схема корзины."""

    firework_id: int
    amount: int


class ReadCartSchema(BaseCartSchema):
    """Схема для чтения корзины пользователя."""

    id: int

    class Config:
        """Прямая работа с атрибутами."""

        from_attributes = True


class CreateCartSchema(BaseCartSchema):
    """Схема для добавления товара в корзину."""

    telegram_id: int


class UpdateCartSchema(BaseModel):
    """Схема для обновления количества товара в корзине."""

    amount: int
    telegram_id: int


class DeleteCartSchema(BaseModel):
    """Схема для удаления товара из корзину."""

    telegram_id: int
