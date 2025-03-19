from pydantic import BaseModel, ConfigDict

from src.schemas.user import TelegramIDSchema


class FavoriteCreate(TelegramIDSchema):
    """Схема запроса на создание."""

    firework_id: int

    model_config = ConfigDict(extra='forbid')


class FireworkSimpleResponse(BaseModel):
    """Схема для отображения данных фейерверка."""

    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class FavoriteDBGet(BaseModel):
    """Схема для получения данных из бд с именем фейерверка."""

    id: int
    firework_id: int
    firework: FireworkSimpleResponse

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FavoriteDBCreate(BaseModel):
    """Схема для добавления в бд."""

    id: int
    firework_id: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
