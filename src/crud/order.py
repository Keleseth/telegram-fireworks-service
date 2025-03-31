from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.crud.cart import cart_crud  # Добавлен импорт для очистки корзины
from src.models.cart import Cart
from src.models.order import Order, OrderFirework
from src.schemas.order import (
    BaseOrderSchema,
    OrderFireworkSchema,
    ReadOrderSchema,
    UpdateOrderAddressSchema,
)


class CRUDOrder(CRUDBase[Order, BaseOrderSchema, UpdateOrderAddressSchema]):
    async def create_order(
        self, db: AsyncSession, user_id: UUID
    ) -> ReadOrderSchema:
        new_order = Order(user_id=user_id, status_id=1, operator_call=False)
        db.add(new_order)
        await db.flush()

        cart_items = (
            (await db.execute(select(Cart).filter(Cart.user_id == user_id)))
            .scalars()
            .all()
        )
        if not cart_items:
            raise HTTPException(status_code=400, detail='Корзина пуста')

        order_fireworks = [
            OrderFirework(
                order_id=new_order.id,
                firework_id=item.firework_id,
                amount=item.amount,
                price_per_unit=item.price_per_unit,
            )
            for item in cart_items
        ]
        db.add_all(order_fireworks)

        # Очистка корзины после создания заказа
        await cart_crud.clear_cart(user_id, db)

        await db.commit()
        await db.refresh(
            new_order, attribute_names=['order_fireworks', 'status']
        )
        return ReadOrderSchema(
            id=new_order.id,
            status=new_order.status.status_text,
            user_address_id=new_order.user_address_id,
            fio=new_order.fio,
            phone=new_order.phone,
            operator_call=new_order.operator_call,
            total=new_order.total,
            order_fireworks=[
                OrderFireworkSchema.model_validate(fw)
                for fw in new_order.order_fireworks
            ],
            user_id=new_order.user_id,
        )

    async def repeat_order_direct(
        self, db: AsyncSession, user_id: UUID, order_id: int
    ) -> ReadOrderSchema:
        old_order = await db.get(Order, order_id)
        if not old_order or old_order.user_id != user_id:
            raise HTTPException(status_code=404, detail='Заказ не найден')

        new_order = Order(
            user_id=user_id,
            status_id=1,
            user_address_id=old_order.user_address_id,
            fio=old_order.fio,
            phone=old_order.phone,
            operator_call=old_order.operator_call,
        )
        db.add(new_order)
        await db.flush()

        order_fireworks = [
            OrderFirework(
                order_id=new_order.id,
                firework_id=item.firework_id,
                amount=item.amount,
                price_per_unit=item.price_per_unit,
            )
            for item in old_order.order_fireworks
        ]
        db.add_all(order_fireworks)
        await db.commit()
        await db.refresh(
            new_order, attribute_names=['order_fireworks', 'status']
        )
        return ReadOrderSchema(
            id=new_order.id,
            status=new_order.status.status_text,
            user_address_id=new_order.user_address_id,
            fio=new_order.fio,
            phone=new_order.phone,
            operator_call=new_order.operator_call,
            total=new_order.total,
            order_fireworks=[
                OrderFireworkSchema.model_validate(fw)
                for fw in new_order.order_fireworks
            ],
            user_id=new_order.user_id,
        )

    async def get_orders_by_user(
        self, db: AsyncSession, user_id: UUID
    ) -> List[ReadOrderSchema]:
        query = (
            select(Order)
            .filter(Order.user_id == user_id)
            .options(
                selectinload(Order.order_fireworks).selectinload(
                    OrderFirework.firework
                ),
                selectinload(Order.status),
            )
        )
        result = await db.execute(query)
        orders = result.scalars().all()
        return [
            ReadOrderSchema(
                id=order.id,
                status=order.status.status_text,
                user_address_id=order.user_address_id,
                fio=order.fio,
                phone=order.phone,
                operator_call=order.operator_call,
                total=order.total,
                order_fireworks=[
                    OrderFireworkSchema.model_validate(fw)
                    for fw in order.order_fireworks
                ],
                user_id=order.user_id,
            )
            for order in orders
        ]

    async def update_order_address(
        self,
        db: AsyncSession,
        user_id: UUID,
        user_address_id: int | None,
        order_id: int,
        address: str | None = None,
        # Оставлен для совместимости, но не используется
        fio: str | None = None,
        phone: str | None = None,
        operator_call: bool = False,
    ) -> ReadOrderSchema:
        query = select(Order).filter(
            Order.id == order_id, Order.user_id == user_id
        )
        order = (await db.execute(query)).scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail='Заказ не найден')
        if user_address_id is not None:
            order.user_address_id = user_address_id
        order.fio = fio
        order.phone = phone
        order.operator_call = operator_call
        await db.commit()
        await db.refresh(order, attribute_names=['order_fireworks', 'status'])
        return ReadOrderSchema(
            id=order.id,
            status=order.status.status_text,
            user_address_id=order.user_address_id,
            fio=order.fio,
            phone=order.phone,
            operator_call=order.operator_call,
            total=order.total,
            order_fireworks=[
                OrderFireworkSchema.model_validate(fw)
                for fw in order.order_fireworks
            ],
            user_id=order.user_id,
        )

    async def update_order_status(
        self, db: AsyncSession, user_id: UUID, status_id: int, order_id: int
    ) -> ReadOrderSchema:
        query = select(Order).filter(
            Order.id == order_id, Order.user_id == user_id
        )
        order = (await db.execute(query)).scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail='Заказ не найден')
        order.status_id = status_id
        await db.commit()
        await db.refresh(order, attribute_names=['order_fireworks', 'status'])
        return ReadOrderSchema(
            id=order.id,
            status=order.status.status_text,
            user_address_id=order.user_address_id,
            fio=order.fio,
            phone=order.phone,
            operator_call=order.operator_call,
            total=order.total,
            order_fireworks=[
                OrderFireworkSchema.model_validate(fw)
                for fw in order.order_fireworks
            ],
            user_id=order.user_id,
        )

    async def delete_order(
        self, db: AsyncSession, user_id: UUID, order_id: int
    ) -> bool:
        query = select(Order).filter(
            Order.id == order_id, Order.user_id == user_id
        )
        order = (await db.execute(query)).scalar_one_or_none()
        if not order or order.status_id != 1:
            return False
        await db.delete(order)
        await db.commit()
        return True


crud_order = CRUDOrder(Order)
