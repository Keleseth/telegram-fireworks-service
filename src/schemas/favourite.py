from uuid import UUID

from pydantic import BaseModel, Extra

from src.schemas.user import TelegramIDSchema


class FavoriteMulti(BaseModel):
    """Базовая схема для передачи в запросе только telegram_id."""

    telegram_id: int

    class Config:
        """Конфиг."""

        extra = Extra.forbid


class FavoriteCreate(TelegramIDSchema):
    """Схема запроса на создание."""

    firework_id: int

    class Config:
        """Конфиг."""

        extra = Extra.forbid


class FavoriteDB(BaseModel):
    """Схема для сохранения в бд."""

    id: int
    user_id: UUID
    firework_id: int

    class Config:
        """Конфиг."""

        orm_mode = True
