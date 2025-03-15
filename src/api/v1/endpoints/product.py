from typing import Union

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.product import category_crud, product_crud
from src.database.db_dependencies import get_async_session
from src.schemas.pagination_schema import (
    MAX_PAGINATION_LIMIT,
    MIN_PAGINATION_LIMIT,
    MIN_PAGINATION_OFFSET,
    PAGINATION_LIMIT,
    PAGINATION_OFFSET,
    PaginationSchema,
)
from src.schemas.product import CategoryCreate, CategoryDB

router = APIRouter()


@router.get(
    '/сategories',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, Union[list[CategoryDB], str, int, None]],
)
async def get_сategories(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    offset: int = Query(PAGINATION_OFFSET, ge=MIN_PAGINATION_OFFSET),
    limit: int = Query(
        PAGINATION_LIMIT, ge=MIN_PAGINATION_LIMIT, le=MAX_PAGINATION_LIMIT
    ),
) -> dict[str, Union[list[CategoryDB], str, int, None]]:
    """Получить все категории фейерверков.

    Доступен всем пользователям.
    """
    pagination_schema = PaginationSchema(offset=offset, limit=limit)
    categories = await category_crud.get_multi(
        session, pagination_schema=pagination_schema
    )
    categories_count = await category_crud.count(session)
    current_url = str(request.url)
    next_page_url = (
        f'{current_url}?offset={offset + limit}&limit={limit}'
        if offset + limit < categories_count
        else None
    )
    previous_page_url = (
        f'{current_url}?offset={
            max(offset - limit, MIN_PAGINATION_OFFSET)
        }&limit={limit}'
        if offset > 0
        else None
    )
    return dict(
        categories=categories,
        next_page_url=next_page_url,
        previous_page_url=previous_page_url,
        categories_count=categories_count,
    )


@router.post(
    '/categories',
    status_code=status.HTTP_201_CREATED,
    response_model=CategoryDB,
)
async def create_category(
    category_schema: CategoryCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Эндпоинт для тестирования базы (не для проды)."""
    return await category_crud.create(category_schema, session)


@router.get(
    '/fireworks',
    status_code=status.HTTP_200_OK,
    response_model=dict[
        str, Union[list[CategoryDB], str, int, None]
    ],  # заменить на кастомную схему
)
async def get_fireworks(
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, Union[list[CategoryDB], str, int, None]]:
    """Получить фейерверки.

    Доступен всем пользователям.
    """
    # TODO: Добавить фильтрацию по тегам, категориям,
    # параметрам, избранным, ценам. Поиск по имени, тегу, артикулу.
    # TODO: Пагинация.
    return await product_crud.get_multi(session=session)


@router.get(
    'fireworks/{firework_id}',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def get_firework_by_id(
    firework_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Получить продукт фейерверк по id.

    Доступен всем пользователям.
    """
    return {'message': 'Запрос выполнен успешно!'}
