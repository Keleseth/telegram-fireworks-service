from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.dependencies import current_admin
from src.crud.user import user_crud
from src.database.db_dependencies import get_async_session
from src.schemas.user import AdminUserUpdate, UserRead

router = APIRouter()


# @router.post('/users/sync-telegram', response_model=UserRead)
# async def create_or_update_or_pass(
#     schema: UserCreate, session: AsyncSession = Depends(get_async_session)
# ):
#     """Создать или обновить пользователя по telegram_id."""
#     user = await user_crud.get_user_id_by_telegram_id(
#         schema_data=schema, session=session
#     )

#     if user:
#         updated_data = schema.create_update_dict()
# has_changes = any(
#     getattr(user, key) != value
#     for key, value in updated_data.items()
# )

#         if has_changes:
#             for key, value in updated_data.items():
#                 setattr(user, key, value)
#             await session.commit()
#             await session.refresh(user)
#     else:
#         user = User(**schema.model_dump())
#         session.add(user)
#         await session.commit()
#         await session.refresh(user)

#     return user


@router.patch(
    '/admin/update-profile/{telegram_id}',
    response_model=UserRead,
    dependencies=[Depends(current_admin)],
)
async def update_admin_profile(
    schema: AdminUserUpdate, session: AsyncSession = Depends(get_async_session)
):
    """Обновить email и пароль админа через менеджер."""
    user = await user_crud.get_user_by_telegram_id(
        telegram_id=schema.telegram_id, session=session
    )
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    return await user_crud.update_admin_user(
        schema_data=schema, user=user, session=session
    )


# router.include_router(
#     fastapi_users.get_auth_router(auth_backend),
#     prefix='/auth/jwt',
#     tags=['auth'],
# )

# router.include_router(
#     fastapi_users.get_register_router(UserRead, UserCreate),
#     prefix='/auth',
#     tags=['auth'],
# )

# router.include_router(
#     fastapi_users.get_users_router(UserRead, UserUpdate),
#     prefix='/users',
#     tags=['users'],
# )
