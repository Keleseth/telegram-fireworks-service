from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """Схема создания обычного пользователя через Telegram."""

    telegram_id: int
    name: str
    nickname: str | None = None
    age_verified: bool


class UserRead(BaseModel):
    """Схема чтения пользователя (возвращаемые данные)."""

    name: str
    nickname: str | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserUpdate(UserCreate):
    """Схема обновления пользователя."""

    telegram_id: int | None = None
    name: str | None = None
    nickname: str | None = None
    age_verified: bool | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminUserUpdate(BaseModel):
    """Схема обновления профиля админа (только email и пароль)."""

    telegram_id: int
    email: EmailStr | None = None
    password: str | None = None


class TelegramIDSchema(BaseModel):
    """Схема для извлечения telegram_id из запроса."""

    telegram_id: int
