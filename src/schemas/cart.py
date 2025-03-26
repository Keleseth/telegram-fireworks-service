from pydantic import BaseModel, ConfigDict, condecimal


class MessageResponse(BaseModel):
    """Базовая схема для ответов."""

    message: str


class FireworkNameSchema(BaseModel):
    """Схема для данных о фейерверке, без id и price."""

    name: str
    price: condecimal(max_digits=10, decimal_places=2)

    model_config = ConfigDict(from_attributes=True)


class UserIdentificationSchema(BaseModel):
    """Базовая схема для telegram_id."""

    telegram_id: int


class BaseCartSchema(BaseModel):
    """Базовая схема корзины."""

    amount: int


class ReadCartSchema(BaseCartSchema):
    """Схема для чтения корзины пользователя."""

    id: int
    firework: FireworkNameSchema

    class Config:
        """Прямая работа с атрибутами."""

        from_attributes = True


class CreateCartSchema(BaseCartSchema):
    """Схема для добавления товара в корзину."""

    firework_id: int


class UpdateCartSchema(UserIdentificationSchema):
    """Схема для обновления количества товара в корзине."""

    amount: int
