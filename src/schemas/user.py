import uuid

from fastapi_users import schemas
from pydantic import EmailStr

# from src.models.user import PreferedLanguage


class UserRead(schemas.BaseUser[uuid.UUID]):
    telegram_id: int | None
    email: EmailStr | None
    age_verified: bool
    name: str
    nickname: str | None
    phone_number: str | None
    # prefered_language: PreferedLanguage
    is_admin: bool
    is_superuser: bool


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr | None = None
    telegram_id: int | None = None
    name: str
    nickname: str | None = None
    phone_number: str | None = None
    # prefered_language: PreferedLanguage = PreferedLanguage.RU
    age_verified: bool = False
    is_admin: bool = False
    is_superuser: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    email: EmailStr | None = None
    telegram_id: int | None = None
    name: str | None = None
    nickname: str | None = None
    phone_number: str | None = None
    # prefered_language: PreferedLanguage | None = None
    age_verified: bool | None = None
    is_admin: bool | None = None
    is_superuser: bool | None = None
