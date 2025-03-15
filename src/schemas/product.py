from typing import Optional

from pydantic import BaseModel, Field, condecimal

MEDIA_TYPE_MIN_LENGTH = 1
MAX_LENGTH = 255
MAX_LENGTH_URL = 512

# Схему Read


class TagSchema(BaseModel):
    name: str


class FireworkBase(BaseModel):
    name: str = Field(..., max_length=MAX_LENGTH)
    tags: list[TagSchema]
    description: Optional[str] = Field(None)
    price: condecimal(ge=0) = Field(...)
    # category_id: Optional[int] = Field(None)
    external_id: str = Field(..., max_length=MAX_LENGTH)
    article: str = Field(...)


class FireworkDB(FireworkBase): ...


class FireworkCreate(FireworkBase):
    pass


class FireworkUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=MAX_LENGTH)
    description: Optional[str] = None
    price: Optional[condecimal(ge=0)] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=MAX_LENGTH_URL)
    video_url: Optional[str] = Field(None, max_length=MAX_LENGTH_URL)
    external_id: Optional[str] = Field(None, max_length=MAX_LENGTH)


class CategoryBase(BaseModel):
    name: str = Field(
        ...,
        max_length=MAX_LENGTH,
    )
    parent_category_id: Optional[int] = Field(
        None,
    )


class CategoryDB(CategoryBase):
    class Config:
        """Конфигурация Pydantic для схемы CategoryDB."""

        from_attributes = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=MAX_LENGTH)
    parent_category_id: Optional[int] = None


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
