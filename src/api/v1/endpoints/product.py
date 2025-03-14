from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.product import product_crud
from src.database.db_dependencies import get_async_session
from src.schemas.product import FireworkBase

router = APIRouter()


@router.get(
    '/сategories',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def get_сategories(
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Получить все категории фейерверков.

    Доступен всем пользователям.
    """
    # TODO: Добвавить пагинацию до 10 категорий за раз.
    return {'message': 'Запрос выполнен успешно!'}


@router.post(
    '/fireworks',
    status_code=status.HTTP_200_OK,
    response_model=list[FireworkBase],  # заменить на кастомную схему
)
async def get_fireworks(
    session: AsyncSession = Depends(get_async_session),
) -> list[FireworkBase]:
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
