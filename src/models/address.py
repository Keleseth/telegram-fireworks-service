import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.database.annotations import int_pk
from src.models import BaseJFModel

if TYPE_CHECKING:
    from src.models.user import User


class Address(BaseJFModel):
    """Модель адресов.

    Поля:
    1. id: int - primary key.
    2. address: Поле адреса, уникальное, обязательное поле.
    """

    id: Mapped[int_pk]
    address: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )

    user_addresses: Mapped[List['UserAddress']] = relationship(
        back_populates='address',
        cascade='all, delete-orphan',
    )


class UserAddress(BaseJFModel):
    """Связующая m-t-m модель между пользователями и адресами.

    Поля:
    1. id: int: primary key.
    2. user_id: ссылка на пользователя, владельца адреса.
    3. address_id: ссылка на адрес, пренадлежащий пользователю.
    """

    id: Mapped[int_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
    )
    address_id: Mapped[int] = mapped_column(
        ForeignKey('address.id', ondelete='CASCADE'), nullable=False
    )
    address: Mapped['Address'] = relationship(back_populates='user_addresses')
    user: Mapped['User'] = relationship(back_populates='addresses')

    __table_args__ = (
        UniqueConstraint('user_id', 'address_id', name='unique_user_address'),
    )
