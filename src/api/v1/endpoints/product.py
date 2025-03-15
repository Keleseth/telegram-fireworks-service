from typing import Union

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.product import category_crud, firework_crud
from src.database.db_dependencies import get_async_session
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


def build_next_and_prev_urls(
    offset: int, limit: int, max_count: int, current_url: str
) -> tuple[str]:
    # с учетом того, что нет других query-параметров.
    clear_url = current_url.split('?')[0]
    next_page_url = (
        f'{clear_url}?offset={offset + limit}&limit={limit}'
        if offset + limit < max_count
        else None
    )
    previous_page_url = (
        f'{clear_url}?offset={
            max(offset - limit, MIN_PAGINATION_OFFSET)
        }&limit={limit}'
        if offset > 0
        else None
    )
    return previous_page_url, next_page_url


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
    previous_page_url, next_page_url = build_next_and_prev_urls(
        offset, limit, categories_count, str(request.url)
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
    """Эндпоинт для тестирования базы (не для проды).

    Создает новую категорию.
    """
    return await category_crud.create(category_schema, session)


@router.get(
    '/fireworks',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, Union[list[FireworkDB], str, int, None]],
)
async def get_fireworks(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    offset: int = Query(PAGINATION_OFFSET, ge=MIN_PAGINATION_OFFSET),
    limit: int = Query(
        PAGINATION_LIMIT, ge=MIN_PAGINATION_LIMIT, le=MAX_PAGINATION_LIMIT
    ),
) -> dict[str, Union[list[FireworkDB], str, int, None]]:
    """Получить фейерверки.

    Доступен всем пользователям.
    """
    # TODO: Добавить фильтрацию по тегам, категориям,
    # параметрам, избранным, ценам. Поиск по имени, тегу, артикулу.
    # TODO: Пагинация.
    pagination_schema = PaginationSchema(offset=offset, limit=limit)
    fireworks = await firework_crud.get_multi(
        session, pagination_schema=pagination_schema
    )
    fireworks_count = await firework_crud.count(session)
    previous_page_url, next_page_url = build_next_and_prev_urls(
        offset, limit, fireworks_count, str(request.url)
    )
    return dict(
        fireworks=fireworks,
        next_page_url=next_page_url,
        previous_page_url=previous_page_url,
        fireworks_count=fireworks_count,
    )


@router.post(
    '/fireworks',
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
    return await firework_crud.get(firework_id, session)
