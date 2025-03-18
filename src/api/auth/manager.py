import os

from dotenv import load_dotenv
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.password import PasswordHelper
from starlette.requests import Request

from src.database.db_dependencies import AsyncSessionLocal
from src.models.user import User
from src.schemas.user import AdminUserUpdate

load_dotenv()

SECRET = os.getenv('SECRET', 'default-secret')


class UserManager(UUIDIDMixin, BaseUserManager):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def update(
        self,
        user_update: AdminUserUpdate,
        user: User,
        safe: bool = True,
        request: Request | None = None,
    ):
        """Обновление пользователя через менеджер."""
        update_data = user_update.model_dump(exclude_unset=True)

        if 'password' in update_data and update_data['password']:
            update_data['hashed_password'] = PasswordHelper().hash(
                update_data.pop('password')
            )

        return await super().update(
            AdminUserUpdate(**update_data), user, safe, request
        )


async def get_user_manager():
    async with AsyncSessionLocal() as session:
        yield UserManager(User, session)
