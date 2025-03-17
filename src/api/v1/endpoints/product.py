from typing import Union

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.utils import build_next_and_prev_urls
from src.api.v1.validators import (
    check_category_exists,
    check_firework_exists,
)
from src.crud.product import category_crud, firework_crud
from src.database.db_dependencies import get_async_session
from src.schemas.filter_shema import FireworkFilterSchema
from src.schemas.pagination_schema import (
    MAX_PAGINATION_LIMIT,
    MIN_PAGINATION_LIMIT,
    MIN_PAGINATION_OFFSET,
    PAGINATION_LIMIT,
    PAGINATION_OFFSET,
    PaginationSchema,
)
from src.schemas.product import (
    CategoryCreate,
    CategoryDB,
    FireworkCreate,
    FireworkDB,
)

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
    categories_count = await category_crud.get_count(session)
    previous_page_url, next_page_url, pages_count = build_next_and_prev_urls(
        offset, limit, categories_count, str(request.url)
    )
    return dict(
        categories=categories,
        next_page_url=next_page_url,
        previous_page_url=previous_page_url,
        pages_count=pages_count,
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
    """Эндпоинт для тестирования базы (не для проды).

    Создает новую категорию.
    """
    return await category_crud.create(category_schema, session)


@router.post(
    '/fireworks',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, Union[list[FireworkDB], str, int, None]],
)
async def get_fireworks(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    filter_schema: FireworkFilterSchema = None,
    offset: int = Query(PAGINATION_OFFSET, ge=MIN_PAGINATION_OFFSET),
    limit: int = Query(
        PAGINATION_LIMIT, ge=MIN_PAGINATION_LIMIT, le=MAX_PAGINATION_LIMIT
    ),
) -> dict[str, Union[list[FireworkDB], str, int, None]]:
    """Получить фейерверки.

    Доступен всем пользователям.
    """
    pagination_schema = PaginationSchema(offset=offset, limit=limit)
    fireworks = await firework_crud.get_multi(
        session,
        pagination_schema=pagination_schema,
        filter_schema=filter_schema,
    )
    fireworks_count = await firework_crud.get_count(session)
    previous_page_url, next_page_url, pages_count = build_next_and_prev_urls(
        offset, limit, fireworks_count, str(request.url)
    )
    return dict(
        fireworks=fireworks,
        next_page_url=next_page_url,
        previous_page_url=previous_page_url,
        pages_count=pages_count,
        fireworks_count=fireworks_count,
    )


@router.get(
    '/fireworks/by_category/{category_id}',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, Union[list[FireworkDB], str, int, None]],
)
async def get_fireworks_by_category_name(
    request: Request,
    category_id: int,
    session: AsyncSession = Depends(get_async_session),
    offset: int = Query(PAGINATION_OFFSET, ge=MIN_PAGINATION_OFFSET),
    limit: int = Query(
        PAGINATION_LIMIT, ge=MIN_PAGINATION_LIMIT, le=MAX_PAGINATION_LIMIT
    ),
):
    await check_category_exists(category_id, session)
    category = await category_crud.get(category_id, session)
    pagination_schema = PaginationSchema(offset=offset, limit=limit)
    filter_schema = FireworkFilterSchema(categories=[category.name])
    fireworks = await firework_crud.get_multi(
        session,
        pagination_schema=pagination_schema,
        filter_schema=filter_schema,
    )
    fireworks_count = len(fireworks)
    previous_page_url, next_page_url, pages_count = build_next_and_prev_urls(
        offset, limit, fireworks_count, str(request.url)
    )
    return dict(
        fireworks=fireworks,
        next_page_url=next_page_url,
        previous_page_url=previous_page_url,
        pages_count=pages_count,
        fireworks_count=fireworks_count,
    )


@router.post(
    '/create_fireworks',
    status_code=status.HTTP_201_CREATED,
    response_model=FireworkDB,
)
async def create_firework(
    firework_schema: FireworkCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Эндпоинт для тестирования базы (не для проды).

    Создает новый фейерверк.
    """
    return await firework_crud.create(firework_schema, session)


@router.get(
    '/fireworks/{firework_id}',
    status_code=status.HTTP_200_OK,
    response_model=FireworkDB,
)
async def get_firework_by_id(
    firework_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> FireworkDB:
    """Получить продукт фейерверк по id.

    Доступен всем пользователям.
    """
    await check_firework_exists(firework_id, session)
    return await firework_crud.get(firework_id, session)
