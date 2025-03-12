from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.address import address_crud
from src.database.db_dependencies import get_async_session
from src.schemas.address import (
    BaseAddressSchema,
    CreateAddressSchema,
    ReadAddressSchema,
    UpdateAddressSchema,
)

router = APIRouter()


@router.post(
    '/addresses',
    status_code=status.HTTP_201_CREATED,
    response_model=BaseAddressSchema,
)
async def create_user_address(
    create_data: CreateAddressSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Создать адрес пользователя."""
    return await address_crud.create(session=session, schema=create_data)


@router.get(
    '/addresses',
    status_code=status.HTTP_200_OK,
    response_model=List[BaseAddressSchema],
)
async def get_user_addressess(
    schema: ReadAddressSchema,  # схема с telegram_id
    session: AsyncSession = Depends(get_async_session),
):
    """Получить адреса пользователя."""
    return await address_crud.get_adresses_by_tg_id(
        session=session, telegram_id=schema.telegram_id
    )


@router.get(
    '/addresses/{address_id}',
    status_code=status.HTTP_200_OK,
    response_model=BaseAddressSchema,
)
async def get_user_address(
    address_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Получить конкретный адрес пользователя по id."""
    return await address_crud.get(session=session, object_id=address_id)


@router.patch(
    '/addresses/{address_id}',
    status_code=status.HTTP_200_OK,
    response_model=BaseAddressSchema,
)
async def update_user_address(
    address_id: str,
    data_update: UpdateAddressSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Изменить адрес пользователя."""
    adress = await address_crud.get(session=session, object_id=address_id)
    return await address_crud.update(
        session=session, schema=data_update, db_object=adress
    )


@router.delete(
    '/address/{address_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=BaseAddressSchema,
)
async def delete_user_address(
    address_id: str,
    schema: ReadAddressSchema,  # схема с telegram_id
    session: AsyncSession = Depends(get_async_session),
):
    """Удалить адрес пользователя."""
    adress = await address_crud.get(session=session, object_id=address_id)
    return await address_crud.remove(
        session=session,
        db_object=adress,
    )
