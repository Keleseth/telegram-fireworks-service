import aiohttp
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.validators import (
    check_formatted_media_exists_by_media_id,
    check_media_exists_by_id,
)
from src.crud.media import formatted_media_crud, media_crud
from src.database.db_dependencies import get_async_session
from src.schemas.media import FormattedMediaCreate, FormattedMediaDB

router = APIRouter()


@router.post(
    '/converted_media/{media_id}',
    response_model=FormattedMediaDB,
    status_code=201,
)
async def create_formatted_media(
    media_id: int, session: AsyncSession = Depends(get_async_session)
) -> FormattedMediaDB:
    media = await media_crud.get(media_id, session)
    await check_media_exists_by_id(media_id, session)
    await check_formatted_media_exists_by_media_id(media_id, session)
    async with aiohttp.ClientSession() as get_media_session:
        async with get_media_session.get(media.media_url) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=400, detail='Ошибка при переходе по media_url!'
                )
            media_data = await response.read()
    formatted_media_create_data = FormattedMediaCreate(
        media_id=media.id, file=media_data
    )
    return await formatted_media_crud.create(
        session, formatted_media_create_data
    )
