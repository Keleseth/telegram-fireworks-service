from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User


class CRUDFavourite:
    async def create_favourite_by_telegram_id(
            self,
            obj_in,
            session: AsyncSession,
    ):
        """Метод для добавления фейерверка в избранное по telegram_id"""
        obj_in_data = obj_in.dict()
        user = await session.scalars(
            select(User).where(
                User.telegram_id == obj_in_data['telegram_id']
            )
        )
        db_obj = self.model(
            user_id=user.id,
            firework_id=obj_in_data['firework_id']
        )
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_multi_by_telegram_id(
            self,
            obj_in,
            session: AsyncSession,
    ):
        """Метод для получения избранных по telegram_id"""
        obj_in_data = obj_in.dict()
        user = await session.scalars(
            select(User).where(
                User.telegram_id == obj_in_data['telegram_id']
            )
        )
        query = select(self.model)
        query = query.order_by(self.model.create_date).where(
            self.model.user_id == user.id
        )
        db_objs = await session.execute(query)
        return db_objs.scalars().all()

    async def remove_by_telegram_id(
            self,
            obj_in,
            firework_id: int,
            session: AsyncSession,
    ):
        """Метод для удаления избранных по telegram_id"""
        obj_in_data = obj_in.dict()
        user = await session.scalars(
            select(User).where(
                User.telegram_id == obj_in_data['telegram_id']
            )
        )
        db_obj = await session.scalar(
            select(self.model).where(
                self.model.user_id == user.id,
                self.model.firework_id == firework_id
            )
        )
        await session.delete(db_obj)
        await session.commit()
        return db_obj
