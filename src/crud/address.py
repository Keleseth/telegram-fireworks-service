from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import and_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase, ModelType
from src.models.address import Address, UserAddress
from src.schemas.address import UpdateAddressSchema


class CRUDAdress(CRUDBase):
    """CRUD-класс для работы с объектами Address."""

    async def get_or_create_address(
        self, address: str, session: AsyncSession
    ) -> Optional[ModelType]:
        """Проверяет наличие адреса и создаёт новый, если такого нет.

        Аргументы:
            1. adress (str): строка адреса.
            2. session (AsyncSession): объект сессии.

        Возвращаемое значение:
            Новый объект Address.
        """
        try:
            new_address = Address(address=address)
            session.add(new_address)
            await session.commit()
            await session.refresh(new_address)
            return new_address
        except IntegrityError:
            await session.rollback()
            result = await session.execute(
                select(Address).where(Address.address == address)
            )
            return result.scalar_one()

    async def get_addresses_by_user_id(
        self, user_id: int, session: AsyncSession
    ) -> Optional[ModelType]:
        """Получает адресса по айди пользователя.

        Аргументы:
            1. user_id (int): айди юзера.
            2. session (AsyncSession): объект сессии.

        Возвращаемое значение:
            Адреса.
        """
        addresses = await session.execute(
            select(Address)
            .join(Address.user_addresses)
            .where(UserAddress.user_id == user_id)
        )
        return addresses.scalars().all()

    async def get_adress_by_id_for_current_user(
        self, user_id: int, address_id: int, session: AsyncSession
    ) -> ModelType | None:
        """Получает адрес для конкретного пользователя.

        Аргументы:
            1. user_id (int): айди юзера.
            2. session (AsyncSession): объект сессии.

        Возвращаемое значение:
            Адрес.
        """
        address = await session.execute(
            select(Address)
            .join(Address.user_addresses)
            .where(
                and_(Address.id == address_id, UserAddress.user_id == user_id)
            )
        )
        address = address.scalar()
        if not address:
            raise HTTPException(
                detail='Нет такого адреса',
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return address

    async def update_adress_by_id(
        self,
        update_data: UpdateAddressSchema,
        address_id: int,
        user_id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        try:
            address = await session.execute(
                update(Address)
                .where(
                    and_(
                        Address.id == address_id,
                        Address.user_addresses.any(
                            UserAddress.user_id == user_id
                        ),
                    )
                )
                .values(address=update_data.address)
                .returning(Address)
            )
            await session.commit()
            await session.refresh(address)
            return address.scalar_one_or_none()
        except IntegrityError as e:
            await session.rollback()
            if 'unique constraint' in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'Адрес уже существует ({e})',
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Ошибка при обновлении адреса ({e})',
            )


class CRUDUserAdress(CRUDBase):
    """CRUD-класс для работы с объектами UserAddress."""

    async def create(
        self,
        address: Address,
        user_id: int,
        session: AsyncSession,
    ) -> UserAddress:
        # Проверяем, существует ли уже такая связь
        user_address_obj = await session.execute(
            select(UserAddress).where(
                (UserAddress.user_id == user_id)
                & (UserAddress.address_id == address.id)
            )
        )
        user_address_obj = user_address_obj.scalar()

        if not user_address_obj:
            new_user_address = UserAddress(
                user_id=user_id, address_id=address.id
            )
            session.add(new_user_address)
            await session.commit()
            await session.refresh(new_user_address)
            return new_user_address
        return user_address_obj

    async def remove(
        self, user_id: int, address_id: int, session: AsyncSession
    ):
        user_address_obj = await session.execute(
            select(UserAddress).where(
                (UserAddress.user_id == user_id)
                & (UserAddress.address_id == address_id)
            )
        )
        user_address_obj = user_address_obj.scalars().first()

        if user_address_obj is None:
            raise HTTPException(
                status_code=404,
                detail='Связь пользователя и адреса не найдена',
            )
        await super().remove(session=session, db_object=user_address_obj)


useraddress_crud = CRUDUserAdress(UserAddress)
address_crud = CRUDAdress(Address)
