from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_user_id
from src.crud.order import crud_order
from src.database.db_dependencies import get_async_session
from src.models.cart import Cart
from src.models.order import Order
from src.schemas.order import (
    DeleteOrderSchema,
    ReadOrderSchema,
    UpdateOrderAddressSchema,
    UpdateOrderStatusSchema,
)

router = APIRouter(prefix='/orders', tags=['orders'])


@router.post('/', response_model=ReadOrderSchema)
async def create_new_order(
    user_id: UUID = Depends(get_user_id),  # user_id получаем через Depends()
    session: AsyncSession = Depends(get_async_session),
):
    """Создать новый заказ из корзины пользователя."""
    return await crud_order.create_order(session, user_id)


@router.post('/{order_id}/repeat', response_model=ReadOrderSchema)
async def repeat_order(
    order_id: int,
    user_id: UUID = Depends(get_user_id),  # user_id через зависимость
    session: AsyncSession = Depends(get_async_session),
):
    """Повторить существующий заказ."""
    return await crud_order.repeat_order(session, user_id, order_id)


@router.post('/me', response_model=List[ReadOrderSchema])
async def get_my_orders(
    user_id: UUID = Depends(get_user_id),  # user_id через зависимость
    session: AsyncSession = Depends(get_async_session),
):
    """Получить список всех заказов пользователя."""
    return await crud_order.get_orders_by_user(session, user_id)


@router.post('/get', response_model=ReadOrderSchema)
async def get_order(
    data: DeleteOrderSchema,  # Только order_id
    user_id: UUID = Depends(get_user_id),  # user_id через зависимость
    session: AsyncSession = Depends(get_async_session),
):
    """Получить заказ по его идентификатору."""
    orders = await crud_order.get_orders_by_user(session, user_id)
    order = next((o for o in orders if o.id == data.order_id), None)
    if order is None:
        raise HTTPException(status_code=404, detail='Заказ не найден')
    return order


@router.patch('/{order_id}/address', response_model=ReadOrderSchema)
async def update_order_address(
    order_id: int,
    data: UpdateOrderAddressSchema,  # Только user_address_id
    user_id: UUID = Depends(get_user_id),  # user_id через зависимость
    session: AsyncSession = Depends(get_async_session),
):
    """Обновить адрес заказа."""
    return await crud_order.update_order_address(
        session, user_id, data.user_address_id, order_id
    )


@router.patch('/{order_id}/status', response_model=ReadOrderSchema)
async def update_order_status(
    order_id: int,
    data: UpdateOrderStatusSchema,  # Только status_id
    user_id: UUID = Depends(get_user_id),  # user_id через зависимость
    session: AsyncSession = Depends(get_async_session),
):
    """Обновить статус заказа."""
    return await crud_order.update_order_status(
        session, user_id, data.status_id, order_id
    )


@router.post('/{order_id}/to_cart')
async def move_order_to_cart(
    order_id: int,
    user_id: UUID = Depends(get_user_id),  # user_id через зависимость
    session: AsyncSession = Depends(get_async_session),
):
    """Переместить товары из заказа в корзину."""
    order = await session.get(Order, order_id)
    if not order or order.user_id != user_id:
        raise HTTPException(status_code=404, detail='Заказ не найден')
    for item in order.order_fireworks:
        session.add(
            Cart(
                user_id=user_id,
                firework_id=item.firework_id,
                amount=item.amount,
            )
        )
    await session.commit()
    return {'detail': 'Товары добавлены в корзину'}


@router.post('/delete')
async def delete_existing_order(
    data: DeleteOrderSchema,  # Только order_id
    user_id: UUID = Depends(get_user_id),  # user_id через зависимость
    session: AsyncSession = Depends(get_async_session),
):
    """Удалить заказ."""
    deleted = await crud_order.delete_order(session, user_id, data.order_id)
    if not deleted:
        raise HTTPException(status_code=400, detail='Невозможно удалить заказ')
    return {'detail': 'Заказ успешно удалён'}
