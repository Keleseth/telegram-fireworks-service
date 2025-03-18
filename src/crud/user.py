from typing import Generic, Optional, TypeVar

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
    ) -> Optional[str]:
        """Возвращает id пользователя по полю telegram_id."""
        result = await session.execute(
            select(self.model.id).filter(
                self.model.telegram_id == schema_data.telegram_id
            )
        )
        return result.scalar_one_or_none()

    async def get_user_by_telegram_id(
        self,
        session: AsyncSession,
        telegram_id: int,
    ) -> Optional[User]:
        """Возвращает пользователя по полю telegram_id."""
        result = await session.execute(
            select(self.model).filter(self.model.telegram_id == telegram_id)
        )
        return result.scalars().first()


user_crud: UserCRUD = UserCRUD(User)
