from typing import Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.base import BaseJFModel
from src.models.favorite import FavoriteFirework
from src.models.user import User
from src.schemas.favourite import FavoriteCreate

ModelType = TypeVar('ModelType', bound=BaseJFModel)


class CRUDFavourite:
    """СRUD-класс для работы с избранными фейерверками."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Инициализирует CRUD-класс с указанной моделью.

        Аргументы:
            model: SQLAlchemy-модель, связанная с таблицей в БД.
        """
        self.model = model

    async def get_user_id_by_telegram_id(
        self,
        obj_in: FavoriteCreate,
        session: AsyncSession,
    ):
        """Метод для получения user_id по telegram_id."""
        obj_in = obj_in.dict()
        return UUID((
            await session.execute(
                select(User.id).where(
                    User.telegram_id == obj_in['telegram_id']
                )
            )
        ).scalar_one_or_none())

    async def create_favourite_by_telegram_id(
        self,
        obj_in: FavoriteCreate,
        user_id: UUID,
        session: AsyncSession,
    ):
        """Метод для добавления фейерверка в избранное по telegram_id."""
        obj_in_data = obj_in.dict()
        if user_id:
            db_obj = self.model(
                user_id=user_id, firework_id=obj_in_data['firework_id']
            )
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_multi_by_telegram_id(
        self,
        user_id: UUID,
        session: AsyncSession,
    ):
        """Метод для получения избранных по telegram_id."""
        print(user_id)
        user_id = UUID("fb310c59-ace1-46cc-a3e4-3b073f47ee45")
        query = (
            select(self.model)
            .options(
                joinedload(self.model.firework)
            )
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at)
        )
        db_objs = await session.execute(query)
        return db_objs.scalars().all()

    async def remove_by_telegram_id(
        self,
        user_id: UUID,
        firework_id: int,
        session: AsyncSession,
    ):
        """Метод для удаления избранных по telegram_id."""
        db_obj = await session.scalar(
            select(self.model).where(
                self.model.user_id == user_id,
                self.model.firework_id == firework_id,
            )
        )
        await session.delete(db_obj)
        await session.commit()
        return db_obj


favorite_crud = CRUDFavourite(FavoriteFirework)
