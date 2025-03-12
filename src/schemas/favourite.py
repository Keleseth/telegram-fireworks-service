from pydantic import BaseModel, Extra


class FavoriteMulti(BaseModel):
    """Базовая схема для передачи в запросе только telegram_id"""
    telegram_id: int

    class Config:
        extra = Extra.forbid


class FavoriteCreate(BaseModel):
    """Схема запроса на создание"""
    firework_id: int
    telegram_id: int

    class Config:
        extra = Extra.forbid


class FavoriteDB(BaseModel):
    """Схема для сохранения в бд"""
    id: int
    user_id: int
    firework_id: int

    class Config:
        orm_mode = True
