from typing import List, Optional, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.base import BaseJFModel
from src.models.bot_info import BotInfo

ModelType = TypeVar('ModelType', bound=BaseJFModel)


class BotInfoCRUD(CRUDBase):
    async def get_multi_bot_info(
        self,
        session: AsyncSession,
    ) -> Optional[List[ModelType]]:
        """Возвращает все объекты модели.

        Аргументы:
            1. session (AsyncSession): объект сессии.
            2. filter_schema (FireworkFilterSchema): схема для фильтрации.

        Возвращаемое значение:
            list[self.model]: список всех объектов модели.
        """
        query = select(self.model)
        bot_info = await session.execute(query)
        return bot_info.scalars().all()


bot_info_crud = BotInfoCRUD(BotInfo)
