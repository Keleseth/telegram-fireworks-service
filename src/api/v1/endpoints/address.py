from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.address import address_crud, useraddress_crud
from src.crud.user import user_crud
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
    address = await address_crud.get_or_create_address(
        session=session, address=create_data.address
    )
    user_id = await user_crud.get_user_id_by_telegram_id(
        schema_data=create_data, session=session
    )
    await useraddress_crud.create(
        session=session,
        address=address,
        user_id=user_id,
    )
    return address


@router.post(
    '/addresses/me',
    status_code=status.HTTP_200_OK,
    response_model=List[BaseAddressSchema],
)
async def get_user_addressess(
    schema: ReadAddressSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Получить адреса юзера."""
    user_id = await user_crud.get_user_id_by_telegram_id(
        session=session, schema_data=schema
    )
    return await address_crud.get_addresses_by_user_id(
        session=session, user_id=user_id
    )


@router.post(
    '/addresses/{address_id}',
    status_code=status.HTTP_200_OK,
    response_model=BaseAddressSchema,
)
async def get_user_address(
    address_id: str,
    schema: ReadAddressSchema,
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
    response_model=BaseAddressSchema,
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
    status_code=status.HTTP_200_OK,
    response_model=BaseAddressSchema,
)
async def delete_user_address(
    address_id: str,
    schema: ReadAddressSchema,
    session: AsyncSession = Depends(get_async_session),
):
    user_id = await user_crud.get_user_id_by_telegram_id(
        session=session, schema_data=schema
    )
    await useraddress_crud.remove(
        session=session, user_id=user_id, address_id=int(address_id)
    )
    return await address_crud.get_adress_by_id_for_current_user(
        session=session, user_id=user_id, address_id=int(address_id)
    )
