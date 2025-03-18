from fastapi_users.schemas import BaseUserUpdate
from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """Схема создания обычного пользователя через Telegram."""

    telegram_id: int
    name: str
    nickname: str | None = None
    age_verified: bool


class UserRead(UserCreate):
    """Схема чтения пользователя (возвращаемые данные)."""

    phone_number: str | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserUpdate(UserCreate):
    """Схема обновления пользователя."""

    telegram_id: int | None = None
    name: str | None = None
    nickname: str | None = None
    age_verified: bool | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminUserUpdate(BaseUserUpdate):
    """Схема обновления профиля админа (только email и пароль)."""

    email: EmailStr | None = None
    password: str | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
