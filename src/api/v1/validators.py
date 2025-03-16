from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.product import category_crud, firework_crud

CHECK_CATEGORY_EXISTS_BY_NAME_ERROR = (
    'Категории с полем (name = {category_name}) не существует!'
)
CHECK_FIREWORK_EXISTS_ERROR = (
    'Фейерверка с полем (id = {firework_id}) не существует!'
)


async def check_category_exists_by_name(
    category_name: str, session: AsyncSession
) -> None:
    category = await category_crud.get_object_by_name(category_name, session)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=CHECK_CATEGORY_EXISTS_BY_NAME_ERROR.format(
                category_name=category_name
            ),
        )


async def check_firework_exists(
    firework_id: int, session: AsyncSession
) -> None:
    firework = await firework_crud.get(firework_id, session)
    if not firework:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=CHECK_FIREWORK_EXISTS_ERROR.format(firework_id=firework_id),
        )
