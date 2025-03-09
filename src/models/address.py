import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.models import BaseJFModel

if TYPE_CHECKING:
    from src.models.order import Order
    from src.models.user import User


class Address(BaseJFModel):
    counter: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    street: Mapped[str] = mapped_column(String(200), nullable=False)
    house_number: Mapped[int] = mapped_column(Integer, nullable=False)

    user_addresses: Mapped[List['UserAddress']] = relationship(
        back_populates='address',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )


class UserAddress(BaseJFModel):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey('user.id'), nullable=False
    )
    address_id: Mapped[int] = mapped_column(
        ForeignKey('address.id'), nullable=False
    )

    address: Mapped['Address'] = relationship(
        back_populates='user_addresses',
        passive_deletes=True,
    )
    user: Mapped['User'] = relationship(
        'User', back_populates='addresses', passive_deletes=True
    )
    orders: Mapped[List['Order']] = relationship(
        back_populates='user_address',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
