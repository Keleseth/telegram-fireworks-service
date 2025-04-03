from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.crud.address import address_crud, useraddress_crud
from src.crud.user import user_crud
from src.database.db_dependencies import get_async_session
from src.models.address import UserAddress
from src.schemas.address import (
    CreateAddressSchema,
    DeleteAddressSchema,
    ReadAddressSchema,
    UpdateAddressSchema,
    UserAddressResponseSchema,
)

router = APIRouter()


@router.post(
    '/addresses',
    status_code=status.HTTP_201_CREATED,
    response_model=UserAddressResponseSchema,
)
async def create_user_address(
    create_data: CreateAddressSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Создать адрес пользователя."""
    address = await address_crud.get_or_create_address(
        session=session, address=create_data.address
    )
    user_id = await user_crud.get_user_id_by_telegram_id(
        schema_data=create_data, session=session
    )
    user_address = await useraddress_crud.create(
        session=session,
        address=address,
        user_id=user_id,
    )
    return {'user_address_id': user_address.id, 'address': address.address}



@router.post(
    '/useraddresses/me',
    status_code=status.HTTP_200_OK,
    response_model=List[UserAddressResponseSchema],
)
async def get_user_address_ids(
    schema: DeleteAddressSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Получить все связи useraddress для пользователя."""
    user_id = await user_crud.get_user_id_by_telegram_id(
        session=session, schema_data=schema
    )
    result = await session.execute(
        select(UserAddress)
        .where(UserAddress.user_id == user_id)
        .options(joinedload(UserAddress.address))
        # Подгружаем отношение address
    )
    user_addresses = result.scalars().all()
    return [
        {'user_address_id': ua.id, 'address': ua.address.address}
        for ua in user_addresses
    ]


@router.post(
    '/addresses/{address_id}',
    status_code=status.HTTP_200_OK,
    response_model=ReadAddressSchema,  # Возвращаем id и address
)
async def get_user_address(
    address_id: str,
    schema: DeleteAddressSchema,  # Используем telegram_id
    session: AsyncSession = Depends(get_async_session),
):
    """Получить конкретный адрес пользователя по id."""
    user_id = await user_crud.get_user_id_by_telegram_id(
        session=session, schema_data=schema
    )
    return await address_crud.get_adress_by_id_for_current_user(
        session=session,
        user_id=user_id,
        address_id=int(address_id),
    )


@router.patch(
    '/addresses/{address_id}',
    status_code=status.HTTP_200_OK,
    response_model=ReadAddressSchema,  # Возвращаем id и address
)
async def update_user_address(
    address_id: str,
    data_update: UpdateAddressSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Изменить адрес пользователя."""
    user_id = await user_crud.get_user_id_by_telegram_id(
        session=session, schema_data=data_update
    )
    await useraddress_crud.remove(
        session=session, user_id=user_id, address_id=int(address_id)
    )
    address = await address_crud.get_or_create_address(
        session=session, address=data_update.address
    )
    await useraddress_crud.create(
        session=session,
        address=address,
        user_id=user_id,
    )
    return address


@router.delete(
    '/address/{address_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_address(
    address_id: str,
    schema: DeleteAddressSchema,  # Используем telegram_id
    session: AsyncSession = Depends(get_async_session),
):
    """Удалить адрес пользователя."""
    user_id = await user_crud.get_user_id_by_telegram_id(
        session=session, schema_data=schema
    )
    await useraddress_crud.remove(
        session=session, user_id=user_id, address_id=int(address_id)
    )
