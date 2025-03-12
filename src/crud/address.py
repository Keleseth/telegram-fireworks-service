from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase, ModelType
from src.models.address import Address
from src.models.user import User


class CRUDAdress(CRUDBase):
    """CRUD-класс для работы с адресами."""

    async def get_adresses_by_tg_id(
        self, telegram_id: int, session: AsyncSession
    ) -> Optional[ModelType]:
        """Получение списка адресов по telegram_id юзера.

        Аргументы:
            1. telegram_id (int): id юзера.
            2. session (AsyncSession): объект сессии.

        Возвращаемое значение:
            self.model: объект модели.
        """
        user_id = await session.execute(
            select(User.id).where(User.telegram_id == telegram_id)
        )
        user_id = user_id.scalars().first()
        return await session.execute(
            select(self.model).where(
                self.model.user_addresses.user_id == user_id
            )
        )


address_crud = CRUDAdress(Address)
