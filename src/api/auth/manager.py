import uuid
from typing import Optional

from fastapi import Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models.user import User


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = 'SECRET'
    verification_token_secret = 'SECRET'

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ):
        print(f'User {user.id} registered.')


engine = create_async_engine(settings.database_url)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_user_manager():
    async with AsyncSessionLocal() as session:
        yield UserManager(session)
