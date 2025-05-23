from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from fastapi import HTTPException
from fastapi_users.password import PasswordHelper
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.user import User
from src.schemas.user import (
    AdminUserUpdate,
    BaseUserUpdate,
    TelegramIDSchema,
)

ModelType = TypeVar('ModelType')
SchemaType = TypeVar('SchemaType', bound=TelegramIDSchema)


class UserCRUD(Generic[ModelType, SchemaType]):
    """CRUD-класс для работы с пользователями."""

    def __init__(self, model: type[User]) -> None:
        """Инициализирует CRUD-класс с указанной моделью.

        Аргументы:
            model: SQLAlchemy-модель, связанная с таблицей в БД.
        """
        self.model = model

    async def get_user_id_by_telegram_id(
        self,
        schema_data: SchemaType,
        session: AsyncSession,
    ) -> Optional[UUID]:
        result = await session.execute(
            select(self.model.id).filter(
                self.model.telegram_id == schema_data.telegram_id
            )
        )
        result = result.scalar_one_or_none()
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Пользователь с указанным telegram_id не найден"
            )
        return result

    async def get_user_by_telegram_id(
        self,
        telegram_id: int,
        session: AsyncSession,
    ) -> Optional[User]:
        """Возвращает пользователя по полю telegram_id."""
        result = await session.execute(
            select(self.model).filter(self.model.telegram_id == telegram_id)
        )
        return result.scalars().first()

    async def update_admin_user(
        self,
        schema_data: AdminUserUpdate,
        user: User,
        session: AsyncSession,
    ) -> User:
        update_data = schema_data.model_dump(exclude_unset=True)
        if update_data.get('password'):
            update_data['hashed_password'] = PasswordHelper().hash(
                update_data.pop('password')
            )
        for key, value in update_data.items():
            setattr(user, key, value)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def telegram_update(
        self, session: AsyncSession, db_obj: User, obj_in: BaseUserUpdate
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_all_users_admin(
        self,
        session: AsyncSession,
    ) -> List[User]:
        """Возвращает пользователей админов."""
        admins = await session.execute(
            select(User).where(User.is_admin.is_(True))
        )
        return admins.scalars().all()


user_crud: UserCRUD = UserCRUD(User)
