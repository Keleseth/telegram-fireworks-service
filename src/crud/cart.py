from typing import List
from uuid import UUID

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
        print(user_id, firework_id)
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
        else:
            firework = await session.get(Firework, schema.firework_id)
            if firework is None:
                raise HTTPException(
                    status_code=404, detail='Фейерверк не найден'
                )
            cart_item = Cart(
                user_id=user_id,
                firework_id=schema.firework_id,
                amount=schema.amount,
                price_per_unit=firework.price,
            )
            session.add(cart_item)
        await session.commit()
        await session.refresh(cart_item)
        return cart_item

    async def update_cart_item(
        self,
        user_id: UUID,
        firework_id: int,
        schema: UpdateCartSchema,
        session: AsyncSession,
    ) -> Cart | None:
        """Обновляет количество товара в корзине."""
        try:
            cart_item = await self.get_cart_item(user_id, firework_id, session)
            if not cart_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Товар не найден в корзине',
                )

            if schema.amount > 0:
                cart_item.amount = schema.amount
                await session.commit()
                await session.refresh(cart_item)
                return cart_item

            await session.delete(cart_item)
            await session.commit()
            return None

        except Exception as e:
            print(f'Ошибка при обновлении товара: {e}')
            raise HTTPException(
                status_code=500, detail='Ошибка при обновлении товара'
            )

    async def remove(
        self, user_id: UUID, firework_id: int, session: AsyncSession
    ) -> None:
        """Удаляет конкретный товар в корзине."""
        cart_item = await self.get_cart_item(user_id, firework_id, session)
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Товар не найден в корзине',
            )
        await session.delete(cart_item)
        await session.commit()

    async def clear_cart(self, user_id: UUID, session: AsyncSession) -> None:
        result = await session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        cart_items = result.scalars().all()
        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Корзина уже пуста.',
            )
        await session.execute(
            self.model.__table__.delete().where(self.model.user_id == user_id)
        )
        await session.commit()


cart_crud = CRUDCart(Cart)
