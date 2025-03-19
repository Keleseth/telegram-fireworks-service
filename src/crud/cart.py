from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.cart import Cart
from src.models.product import Firework
from src.schemas.cart import CreateCartSchema, UpdateCartSchema


class CRUDCart(CRUDBase[Cart, CreateCartSchema, UpdateCartSchema]):
    """CRUD-операции для работы с корзиной."""

    async def get_by_user(
        self, user_id: int, session: AsyncSession
    ) -> List[Cart]:
        """Получает все товары в корзине конкретного пользователя."""
        result = await session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return result.scalars().all()

    async def get_cart_item(
        self, user_id: int, firework_id: int, session: AsyncSession
    ) -> Cart | None:
        """Получает конкретный товар в корзине пользователя."""
        result = await session.execute(
            select(self.model)
            .where(self.model.user_id == user_id)
            .where(self.model.firework_id == firework_id)
        )
        return result.scalars().first()

    async def add_to_cart(
        self, user_id: int, schema: CreateCartSchema, session: AsyncSession
    ) -> Cart:
        """Добавляет товар в корзину пользователя."""
        cart_item = await self.get_cart_item(
            user_id, schema.firework_id, session
        )

        if cart_item:
            price_per_unit = cart_item.price_per_unit
        else:
            firework = await session.get(Firework, schema.firework_id)
            if firework is None:
                raise HTTPException(
                    status_code=404, detail='Фейерверк не найден'
                )
            price_per_unit = firework.price
        if cart_item:
            cart_item.amount += schema.amount
        else:
            cart_item = Cart(
                user_id=user_id,
                firework_id=schema.firework_id,
                amount=schema.amount,
                price_per_unit=price_per_unit,
            )
            session.add(cart_item)
        await session.commit()
        await session.refresh(cart_item)
        return cart_item

    async def update_cart_item(
        self,
        user_id: int,
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
        self, user_id: int, firework_id: int, session: AsyncSession
    ) -> Cart:
        """Удаляет конкретнsq товар в корзине."""
        cart_item = await self.get_cart_item(user_id, firework_id, session)
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Товар не найден в корзине',
            )
        return await self.remove(cart_item, session)


cart_crud = CRUDCart(Cart)
