from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud_order.create_order(session, user_id)


@router.post('/{order_id}/repeat_direct', response_model=ReadOrderSchema)
async def repeat_order_direct(
    order_id: int,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud_order.repeat_order_direct(session, user_id, order_id)


@router.post('/me', response_model=List[ReadOrderSchema])
async def get_my_orders(
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud_order.get_orders_by_user(session, user_id)


@router.post('/get', response_model=ReadOrderSchema)
async def get_order(
    data: DeleteOrderSchema,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    orders = await crud_order.get_orders_by_user(session, user_id)
    order = next((o for o in orders if o.id == data.order_id), None)
    if order is None:
        raise HTTPException(status_code=404, detail='Заказ не найден')
    return order


@router.patch(
    '/{order_id}/address',
    response_model=ReadOrderSchema,
    status_code=status.HTTP_201_CREATED,
)
async def update_order_address(
    order_id: int,
    data: UpdateOrderAddressSchema,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    print(data.user_address_id, data.fio, data.phone, data.operator_call)
    order = await session.get(Order, order_id)
    if not order or order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Заказ не найден'
        )
    if order.status.status_text == 'Shipped':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нельзя изменить адрес после отправки',
        )
    return await crud_order.update_order_address(
        session,
        user_id,
        data.user_address_id,
        order_id,
        fio=data.fio,
        phone=data.phone,
        operator_call=data.operator_call,
    )


@router.patch('/{order_id}/status', response_model=ReadOrderSchema)
async def update_order_status(
    order_id: int,
    data: UpdateOrderStatusSchema,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud_order.update_order_status(
        session, user_id, data.status_id, order_id
    )


@router.post('/{order_id}/to_cart')
async def move_order_to_cart(
    order_id: int,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    order = await session.get(Order, order_id)
    if not order or order.user_id != user_id:
        raise HTTPException(status_code=404, detail='Заказ не найден')

    for item in order.order_fireworks:
        existing_cart_item = (
            await session.execute(
                select(Cart).filter(
                    Cart.user_id == user_id,
                    Cart.firework_id == item.firework_id,
                )
            )
        ).scalar_one_or_none()

        if existing_cart_item:
            existing_cart_item.amount += item.amount
        else:
            session.add(
                Cart(
                    user_id=user_id,
                    firework_id=item.firework_id,
                    price_per_unit=item.price_per_unit,
                    amount=item.amount,
                )
            )

    await session.commit()
    return {'detail': 'Товары добавлены в корзину'}


@router.get('/{order_id}/delivery_status', response_model=dict)
async def get_delivery_status(
    order_id: int,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    order = await session.get(Order, order_id)
    if (
        not order
        or order.user_id != user_id
        or order.status.status_text != 'Shipped'
    ):
        raise HTTPException(
            status_code=404, detail='Заказ не найден или не отправлен'
        )
    return {'order_id': order_id, 'delivery_status': 'В пути'}
