from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.discounts import ShortDiscountSchema
from src.schemas.media import MediaDB

MEDIA_TYPE_MIN_LENGTH = 1
MAX_LENGTH = 255
MAX_LENGTH_URL = 512


class TagSchema(BaseModel):
    name: str


class CategoryBase(BaseModel):
    name: str = Field(
        ...,
        max_length=MAX_LENGTH,
    )
    parent_category_id: Optional[int] = None


class CategoryDB(CategoryBase):
    id: int

    class Config:
        """Конфигурация Pydantic для схемы CategoryDB."""

        from_attributes = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=MAX_LENGTH)


class FireworkBase(BaseModel):
    code: str = Field(...)
    name: str = Field(..., max_length=MAX_LENGTH)
    measurement_unit: str = Field(...)
    description: Optional[str] = Field(None)
    price: Decimal = Field(...)
    category_id: Optional[int] = Field(None)
    tags: Optional[list[TagSchema]] = Field([])
    charges_count: Optional[int] = Field(None)
    effects_count: Optional[int] = Field(None)
    product_size: str = Field(...)
    packing_material: Optional[str] = Field(None)
    article: str = Field(...)
    discounts: list[ShortDiscountSchema] = Field(None)
    media: list[MediaDB] = Field(None)


class FireworkDB(FireworkBase):
    id: int

    class Config:
        """Конфигурация Pydantic для схемы FireworkDB."""

        from_attributes = True


class FireworkCreate(FireworkBase):
    pass


class FireworkUpdate(BaseModel):
    code: Optional[str] = Field(None)
    name: Optional[str] = Field(None, max_length=MAX_LENGTH)
    measurement_unit: Optional[str] = Field(None)
    price: Decimal = Field(None)
    product_size: Optional[str] = Field(None)
    article: Optional[str] = Field(None)


class TagBase(BaseModel):
    name: str = Field(
        ...,
        max_length=MAX_LENGTH,
    )


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        max_length=MAX_LENGTH,
    )
