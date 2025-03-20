from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Базовая схема для ответов."""

    message: str


class UserIdentificationSchema(BaseModel):
    """Базовая схема для telegram_id."""

    telegram_id: int


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


class CreateCartSchema(BaseCartSchema, UserIdentificationSchema):
    """Схема для добавления товара в корзину."""

    pass


class UpdateCartSchema(BaseModel, UserIdentificationSchema):
    """Схема для обновления количества товара в корзине."""

    amount: int
