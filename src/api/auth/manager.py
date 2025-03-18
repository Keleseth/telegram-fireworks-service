import os

from dotenv import load_dotenv
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.password import PasswordHelper
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.models.user import User
from src.schemas.user import AdminUserUpdate

load_dotenv()

SECRET = os.getenv('SECRET', 'default-secret')


class UserManager(UUIDIDMixin, BaseUserManager):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    def __init__(self, user_db: SQLAlchemyUserDatabase) -> None:
        """Инициализация UserManager с user_db."""
        super().__init__(user_db)

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

        for key, value in update_data.items():
            setattr(user, key, value)

        self.user_db.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user


async def get_user_manager(session: AsyncSession):
    user_db = SQLAlchemyUserDatabase(
        User, session
    )  # Создаём user_db (User идёт первым!)
    yield UserManager(user_db)  # Передаём user_db в менеджер
