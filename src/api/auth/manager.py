import os
import uuid
from typing import Optional

from dotenv import load_dotenv
from fastapi import Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from src.database.db_dependencies import AsyncSessionLocal
from src.models.user import User

load_dotenv()

SECRET = os.getenv('SECRET', 'default-secret')


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ):
        print(f'User {user.id} registered.')


async def get_user_manager():
    async with AsyncSessionLocal() as session:
        yield UserManager(session)
