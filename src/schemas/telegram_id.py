from pydantic import BaseModel


# TODO добавить эту схемы для эндпоинтов проверяющих авторство с валидационной
# функцией.
class TelegramUserSchema(BaseModel):
    """Схема для всех запросов с Telegram ID."""

    telegram_id: int
