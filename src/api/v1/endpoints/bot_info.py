from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.bot_info import bot_info_crud
from src.database.db_dependencies import get_async_session
from src.schemas.bot_info import ReadBotInfoSchema

router = APIRouter()


@router.get(
    '/botinfo',
    status_code=status.HTTP_200_OK,
    response_model=ReadBotInfoSchema,
)
async def get_bot_info(
    session: AsyncSession = Depends(get_async_session),
):
    """Получение информации о боте."""
    return (await bot_info_crud.get_multi(session=session))[0]
