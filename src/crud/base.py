"""Модуль с базовыми классами для CRUD-операций.

Содержит:
- Определения типов: ModelType, CreateSchemaType, UpdateSchemaType.
- Константу COMMIT_ON для управления автокоммитом.
- Класс CRUDBaseREAD с безопасными методами get и get_multi.
- Класс CRUDBase(CRUDBaseREAD) с методами create, update и remove
    для возможности внесения изменений в БД.
"""

from http import HTTPStatus
from typing import Generic, List, Optional, Type, TypeVar

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import BaseJFModel

ModelType = TypeVar('ModelType', bound=BaseJFModel)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


COMMIT_ON = True

CREATE_ERROR_400 = (
    'Нарушена целостность полей создаваемой модели. '
    'Текст ошибки: {error_message}'
)
CREATE_ERROR_500 = (
    'Ошибка сервера про создании нового объекта. Текст ошибки: {error_message}'
)

UPDATE_ERROR_400 = (
    'Нарушена целостность полей обновляемой модели. '
    'Текст ошибки: {error_message}'
)
UPDATE_ERROR_500 = (
    'Ошибка сервера при обновлении объекта. Текст ошибки: {error_message}'
)

DELETE_ERROR_500 = (
    'Ошибка сервера при удалении объекта. Текст ошибки: {error_message}'
)


class CRUDBaseRead(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый CRUD-класс только с безопасными методами."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Инициализирует CRUD-класс с указанной моделью.

        Аргументы:
            model: SQLAlchemy-модель, связанная с таблицей в БД.
        """
        self.model = model

    async def get_multi(
        self,
        session: AsyncSession,
    ) -> Optional[List[ModelType]]:
        """Возвращает все объекты модели.

        Аргументы:
            session (AsyncSession): объект сессии.
            filters (dict): словарь с полями фильтрации.

        Возвращаемое значение:
            list[self.model]: список всех объектов модели.
        """
        return (await session.execute(select(self.model))).scalars().all()

    async def get(
        self, object_id: int, session: AsyncSession
    ) -> Optional[ModelType]:
        """Получение объекта по id.

        Аргументы:
            object_id (int): id объекта.
            session (AsyncSession): объект сессии.

        Возвращаемое значение:
            self.model: объект модели.
        """
        return await session.execute(
            select(self.model).where(self.model.id == object_id)
        )


class CRUDBase(CRUDBaseRead):
    """Базовый CRUD-класс."""

    async def create(
        self,
        schema: CreateSchemaType,
        session: AsyncSession,
        commit_on: bool = COMMIT_ON,
    ) -> ModelType:
        """Создаёт новый объект в БД.

        Аргументы:
            schema: Pydantic-схема.
            session (AsyncSession): объект сессии.
            commit_on (bool, optional): настройка фиксации изменений в БД.
                - по умолчанию True.

        Возвращаемое значение:
            self.model: созданный объект модели.
        """
        schema_data = schema.model_dump()
        db_object = self.model(**schema_data)
        try:
            session.add(db_object)
            if commit_on:
                await session.commit()
                await session.refresh(db_object)
            return db_object
        except IntegrityError as error:
            await session.rollback()
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=CREATE_ERROR_400.format(error_message=str(error)),
            )
        except SQLAlchemyError as error:
            await session.rollback()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=CREATE_ERROR_500.format(error_message=str(error)),
            )

    async def update(
        self,
        db_object: ModelType,
        schema: UpdateSchemaType,
        session: AsyncSession,
        commit_on: bool = COMMIT_ON,
    ) -> ModelType:
        """Обновляет существующий объект (частичное обновление).

        Аргументы:
            db_object: обновляемый объект.
            schema: Pydantic-схема.
            session (AsyncSession): объект сессии.
            commit_on (bool, optional): настройка фиксации изменений в БД.
                - по умолчанию True.

        Возвращаемое значение:
            self.model: обновленный объект.
        """
        object_data = jsonable_encoder(db_object)
        update_data = schema.model_dump(exclude_unset=True)
        for field in object_data:
            if field in update_data:
                setattr(db_object, field, update_data[field])
        try:
            session.add(db_object)
            if commit_on:
                await session.commit()
                await session.refresh(db_object)
            return db_object
        except IntegrityError as error:
            await session.rollback()
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=UPDATE_ERROR_400.format(error_message=str(error)),
            )
        except SQLAlchemyError as error:
            await session.rollback()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=UPDATE_ERROR_500.format(error_message=str(error)),
            )

    async def remove(
        self,
        db_object: ModelType,
        session: AsyncSession,
        commit_on: bool = COMMIT_ON,
    ) -> ModelType:
        """Удаляет переданный объект.

        Аргументы:
            db_object: удаляемый объект.
            session (AsyncSession): объект сессии.
            commit_on (bool, optional): настройка фиксации изменений в БД.
                - по умолчанию True.

        Возвращаемое значение:
            self.model: удаленная модель.
        """
        try:
            await session.delete(db_object)
            if commit_on:
                await session.commit()
            return db_object
        except SQLAlchemyError as error:
            await session.rollback()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=DELETE_ERROR_500.format(error_message=str(error)),
            )
