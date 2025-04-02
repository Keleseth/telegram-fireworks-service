from typing import Optional, Type, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBaseRead
from src.models.base import BaseJFModel
from src.models.media import FormattedMedia, Media
from src.schemas.media import FormattedMediaCreate, MediaCreate, MediaUpdate

ModelType = TypeVar('ModelType', bound=BaseJFModel)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class FormattedMediaCRUD:
    """CRUD для работы с медиа."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Инициализатор FormattedMedia круда."""
        self.model = model

    async def create(
        self,
        session: AsyncSession,
        formatted_media_schema: FormattedMediaCreate,
    ) -> ModelType:
        schema_data = formatted_media_schema.model_dump()
        db_object = self.model(
            file=schema_data.file, media_id=schema_data.media_id
        )
        try:
            session.add(db_object)
            await session.commit()
            await session.refresh(db_object)
            return db_object
        except IntegrityError as error:
            await session.rollback()
            raise HTTPException(
                code=400, detail=f'Ошибка в данных: {str(error)}'
            )
        except SQLAlchemyError as error:
            await session.rollback()
            raise HTTPException(
                code=500, detail=f'Ошибка сервера! Текст ошибки: {str(error)}'
            )

    async def get_by_media_id(
        self, media_id: int, session: AsyncSession
    ) -> Optional[FormattedMedia]:
        return (
            await session.execute(
                select(FormattedMedia).where(
                    FormattedMedia.media_id == media_id
                )
            )
        ).scalar()


class MediaCRUD(CRUDBaseRead[Media, MediaCreate, MediaUpdate]): ...


formatted_media_crud = FormattedMediaCRUD(FormattedMedia)
media_crud = CRUDBaseRead(Media)
