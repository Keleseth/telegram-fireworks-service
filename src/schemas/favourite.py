from pydantic import BaseModel, Extra, Field

from src.schemas.user import TelegramIDSchema


class FavoriteCreate(TelegramIDSchema):
    """Схема запроса на создание."""

    firework_id: int

    class Config:
        """Конфиг."""

        extra = Extra.forbid


class FavoriteDB(BaseModel):
    """Схема для сохранения в бд."""

    id: int
    firework_id: int
    firework_name: str = Field(alias="firework.name")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
