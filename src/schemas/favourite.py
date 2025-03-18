from pydantic import BaseModel, Extra

from src.schemas.user import TelegramIDSchema


class FavoriteCreate(TelegramIDSchema):
    """Схема запроса на создание."""

    firework_id: int

    class Config:
        """Конфиг."""

        extra = Extra.forbid


class FireworkSimpleResponse(BaseModel):
    """Схема для отображения данных фейерверка."""

    id: int
    name: str

    class Config:
        """Конфиг."""

        orm_mode = True


class FavoriteDBGet(BaseModel):
    """Схема для получения данных из бд с именем фейерверка."""

    id: int
    firework_id: int
    firework: FireworkSimpleResponse

    class Config:
        """Конфиг."""

        orm_mode = True
        allow_population_by_field_name = True


class FavoriteDBCreate(BaseModel):
    """Схема для добавления в бд."""

    id: int
    firework_id: int

    class Config:
        """Конфиг."""

        orm_mode = True
        allow_population_by_field_name = True
