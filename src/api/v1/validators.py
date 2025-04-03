from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.media import formatted_media_crud, media_crud
from src.crud.product import firework_crud

CHECK_CATEGORY_EXISTS_ERROR = (
    'Категории с полем (id = {category_id}) не существует!'
)
CHECK_FIREWORK_EXISTS_ERROR = (
    'Фейерверка с полем (id = {firework_id}) не существует!'
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


async def check_category_exists(
    category_id: int, session: AsyncSession
) -> None:
    firework = await firework_crud.get(category_id, session)
    if not firework:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=CHECK_CATEGORY_EXISTS_ERROR.format(category_id=category_id),
        )


async def check_media_exists_by_id(
    media_id: int, session: AsyncSession
) -> None:
    media = await media_crud.get(media_id, session)
    if not media:
        raise HTTPException(
            status_code=400, detail=f'Медиа с id={media_id} не существует!'
        )


async def check_formatted_media_exists_by_media_id(
    media_id: int, session: AsyncSession
) -> None:
    formatted_media = await formatted_media_crud.get_by_media_id(
        media_id, session
    )
    if formatted_media:
        raise HTTPException(
            status_code=400,
            detail=(
                f'Отформатировванное медиа с media_id={media_id}'
                f' уже существует!'
            ),
        )
