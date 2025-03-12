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
from sqlalchemy import and_, asc, desc, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.query import Query

from src.models.base import BaseJFModel
from src.models.product import Tag
from src.schemas.filter_shema import FireworkFilterSchema

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

    def apply_filters(
        self, query: Query, filter_schema: FireworkFilterSchema
    ) -> Query:
        """Добавляет фильтры к запросу."""
        filters = []
        if filter_schema.name:
            filters.append(self.model.name == filter_schema.name)
        if filter_schema.number_of_volleys:
            filters.append(
                self.number_of_volleys == filter_schema.number_of_volleys
            )
        if filter_schema.categories:
            # Получаем продукты,
            # которые есть в перечисленных категориях.
            filters.append(
                self.model.category.name.in_(filter_schema.categories)
            )
        if filter_schema.article:
            filters.append(self.model.article == filter_schema.article)
        if filter_schema.tags:
            # Получаем продукты,
            # у которых хотя бы 1 тег есть в перечисленных.
            filters.append(
                self.model.tags.any(Tag.name.in_(filter_schema.tags))
            )
        if filter_schema.min_price:
            filters.append(self.model.price >= filter_schema.min_price)
        if filter_schema.max_price:
            filters.append(self.model.price <= filter_schema.max_price)
        if filters:
            query = query.where(and_(*filters))
        return query

    def apply_sort(self, query: Query, order_by_fields: list[str]) -> Query:
        """Добавляет сортировку к запросу."""
        ordering = []
        for sorted_field in order_by_fields:
            if sorted_field.startswith('-'):
                ordering.append(desc(getattr(self.model, sorted_field[1:])))
            else:
                ordering.append(asc(getattr(self.model, sorted_field)))
        return query.order_by(*ordering)

    async def get_multi(
        self,
        session: AsyncSession,
        filter_schema: Optional[FireworkFilterSchema] = None,
    ) -> Optional[List[ModelType]]:
        """Возвращает все объекты модели.

        Аргументы:
            1. session (AsyncSession): объект сессии.
            2. filter_schema (FireworkFilterSchema): схема для фильтрации.

        Возвращаемое значение:
            list[self.model]: список всех объектов модели.
        """
        query = select(self.model)
        if filter_schema:
            query = self.apply_filters(query, filter_schema)
        if filter_schema.order_by:
            query = self.apply_sort(query, filter_schema.order_by)
        fireworks = await session.execute(query)
        return fireworks.scalars().all()

    async def get(
        self, object_id: int, session: AsyncSession
    ) -> Optional[ModelType]:
        """Получение объекта по id.

        Аргументы:
            1. object_id (int): id объекта.
            2. session (AsyncSession): объект сессии.

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
            1. schema: Pydantic-схема.
            2. session (AsyncSession): объект сессии.
            3. commit_on (bool, optional): настройка фиксации изменений в БД.
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
            1. db_object: обновляемый объект.
            2. schema: Pydantic-схема.
            3. session (AsyncSession): объект сессии.
            4. commit_on (bool, optional): настройка фиксации изменений в БД.
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
            1. db_object: удаляемый объект.
            2. session (AsyncSession): объект сессии.
            3. commit_on (bool, optional): настройка фиксации изменений в БД.
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
