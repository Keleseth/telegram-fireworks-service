import re
from typing import Optional, Union

from fastapi import Depends, HTTPException, Request, status
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.password import PasswordHelper
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database.db_dependencies import get_async_session
from src.models.user import User
from src.schemas.user import BaseUserUpdate, UserCreate


class UserManager(UUIDIDMixin, BaseUserManager):
    """Мэнеджер для управления пользователями."""

    reset_password_token_secret = settings.reset_password_token_secret
    verification_token_secret = settings.verification_token_secret

    def __init__(self, user_db: SQLAlchemyUserDatabase) -> None:
        """Инициализация UserManager с user_db."""
        super().__init__(user_db)

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ):
        print(f'Пользователь {user.id} зарегистрирован.')

    async def validate_password(
        self, password: str, user: Union[UserCreate, User]
    ) -> None:
        """Валидатор для пароля."""
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Пароль должен иметь больше 8 символов',
            )
        if not re.search(r'[A-Z]', password) or not re.search(r'\d', password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Пароль должен содержать заглавную букву и цифру.',
            )

    async def create(
        self,
        user_create: UserCreate,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> User:
        """Создание пользователя в базе данных.

        Через менеджер на основе данных из Telegram.
        """
        user_dict = user_create.model_dump(exclude_unset=True)
        if user_dict['age_verified'] is True:
            user_dict.setdefault('is_active', True)
        user_dict.setdefault('is_verified', True)
        return await self.user_db.create(user_dict)

    async def update(
        self,
        user_update: BaseUserUpdate,
        user: User,
        safe: bool = True,
        request: Request | None = None,
    ):
        """Обновление пользователя в базе данных через менеджер."""
        update_data = user_update.model_dump(exclude_unset=True)
        if 'password' in update_data and update_data['password']:
            update_data['hashed_password'] = PasswordHelper().hash(
                update_data.pop('password')
            )
        else:
            update_data['hashed_password'] = None
        if user.is_superuser or user.is_admin:
            update_data['age_verified'] = True
        return await self.user_db.update(user, update_data)


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db=Depends(get_user_db)):  # noqa: ANN001
    yield UserManager(user_db)
