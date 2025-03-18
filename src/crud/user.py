from typing import Generic, Optional, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.user import User
from src.schemas.user import TelegramIDSchema

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
        return result.scalar_one_or_none()


user_crud: UserCRUD = UserCRUD(User)
