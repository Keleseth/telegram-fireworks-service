from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.cart import Cart
from src.schemas.cart import CreateCartSchema, UpdateCartSchema


class CRUDCart(CRUDBase[Cart, CreateCartSchema, UpdateCartSchema]):
    """CRUD-операции для работы с корзиной."""

    async def get_by_user(
        self, user_id: UUID, session: AsyncSession
    ) -> List[Cart]:
        """Получает все товары в корзине конкретного пользователя."""
        result = await session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return result.scalars().all()

    async def get_cart_item(
        self, user_id: UUID, firework_id: int, session: AsyncSession
    ) -> Cart | None:
        """Получает конкретный товар в корзине пользователя."""
        result = await session.execute(
            select(self.model)
            .where(self.model.user_id == user_id)
            .where(self.model.firework_id == firework_id)
        )
        return result.scalars().first()

    async def add_to_cart(
        self, user_id: UUID, schema: CreateCartSchema, session: AsyncSession
    ) -> Cart:
        """Добавляет товар в корзину пользователя."""
        cart_item = await self.get_cart_item(
            user_id, schema.firework_id, session
        )
        if cart_item:
            cart_item.amount += schema.amount
            return await self.update(
                cart_item, UpdateCartSchema(amount=cart_item.amount), session
            )
        return await self.create(
            CreateCartSchema(**schema.model_dump(), user_id=user_id), session
        )

    async def update_cart_item(
        self,
        user_id: UUID,
        firework_id: int,
        schema: UpdateCartSchema,
        session: AsyncSession,
    ) -> List[Cart]:
        """Обновляет количество конкретного товара в корзине."""
        cart_item = await self.get_cart_item(user_id, firework_id, session)
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Товар не найден в корзине',
            )
        return await self.update(cart_item, schema, session)

    async def remove(
        self, user_id: UUID, firework_id: int, session: AsyncSession
    ) -> Cart:
        """Удаляет конкретный товар в корзине."""
        cart_item = await self.get_cart_item(user_id, firework_id, session)
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Товар не найден в корзине',
            )
        return await super().remove(cart_item, session)


cart_crud = CRUDCart(Cart)
