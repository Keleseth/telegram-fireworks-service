from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import InvalidPasswordException, exceptions
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.auth import (
    create_refresh_token,
    get_jwt_strategy,
    redis_client,
    verify_refresh_token,
)
from src.api.auth.dependencies import (
    current_admin,
    current_admin_with_token,
    current_user,
)
from src.api.auth.manager import UserManager, get_user_manager
from src.crud.user import user_crud
from src.database.db_dependencies import get_async_session
from src.models import User
from src.schemas.user import (
    AdminUserUpdate,
    BaseUserUpdate,
    TelegramAdminUserRead,
    TelegramAdminUserUpdate,
    TelegramIDSchema,
    UserCreate,
    UserRead,
    UserReadForTelegram,
    UserUpdate,
)

router = APIRouter()


@router.post(
    '/users',
    status_code=status.HTTP_200_OK,
    response_model=UserReadForTelegram,
    responses={404: {'description': 'User not found'}},
)
async def get_user(
    user_telegram_id: TelegramIDSchema,
    session: AsyncSession = Depends(get_async_session),
):
    user = await user_crud.get_user_by_telegram_id(
        session=session, telegram_id=user_telegram_id.telegram_id
    )
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@router.patch(
    '/users',
    status_code=status.HTTP_200_OK,
    response_model=UserReadForTelegram,
    responses={
        404: {'description': 'User not found'},
        403: {'description': 'Forbidden'},
    },
)
async def update_user_parameters(
    update_data: BaseUserUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    user = await user_crud.get_user_by_telegram_id(
        session=session, telegram_id=update_data.telegram_id
    )
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    return await user_crud.telegram_update(
        session=session, db_obj=user, obj_in=update_data
    )


@router.post(
    '/moderator',
    status_code=status.HTTP_200_OK,
    response_model=TelegramAdminUserRead,
    responses={404: {'description': 'User not found'}},
)
async def get_admin_user(
    user_telegram_id: TelegramIDSchema,
    session: AsyncSession = Depends(get_async_session),
):
    user = await user_crud.get_user_by_telegram_id(
        session=session, telegram_id=user_telegram_id.telegram_id
    )
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@router.patch(
    '/moderator/{user_telegram_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserReadForTelegram,
    responses={
        404: {'description': 'User not found'},
        403: {'description': 'Forbidden'},
    },
)
async def update_admin_user_parameters(
    user_telegram_id: int,
    update_data: TelegramAdminUserUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    user = await user_crud.get_user_by_telegram_id(
        session=session, telegram_id=user_telegram_id
    )
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    return await user_crud.telegram_update(
        session=session, db_obj=user, obj_in=update_data
    )


@router.post(
    '/auth/telegram-register',
    response_model=UserRead,
)
async def user_create(
    user_create: UserCreate,
    user_manager: UserManager = Depends(get_user_manager),
):
    """Эндпоинт для создания пользователя через Telegram.

    Ожидает UserCreate с telegram_id.
    """
    try:
        user = await user_manager.create(user_create, safe=True)
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пользователь уже существует.',
        )
    return user


@router.patch(
    '/moderator/update-profile/',
    response_model=UserRead,
)
async def update_admin_profile(
    admin_schema: AdminUserUpdate,
    admin: User = Depends(current_admin),
    user_manager: UserManager = Depends(get_user_manager),
):
    """Обновить email и пароль админа через менеджер."""
    return await user_manager.update(
        user_update=admin_schema,
        user=admin,
        safe=True,
    )


@router.patch(
    '/user/update-profile/',
    response_model=UserRead,
    summary='Обновление профиля пользователя через Telegram',
)
async def update_user_profile(
    user_schema: UserUpdate,
    telegram_user: User = Depends(current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    """Обновить профиль пользователя, включая адрес."""
    return await user_manager.update(
        user_update=user_schema,
        user=telegram_user,
        safe=True,
    )


@router.post('/auth/jwt/login')
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_manager: UserManager = Depends(get_user_manager),
):
    """Кастомный эндпоинт для получения токена.

    Параметры функции:
    1) form_data - данные формы с username и password;
    2) user_manager - пользовательский менеджер.
    """
    user = await user_manager.get_by_email(form_data.username)
    if user is None:
        raise HTTPException(
            status_code=401, detail='Неверный email или пароль'
        )
    try:
        await user_manager.validate_password(form_data.password, user)
    except InvalidPasswordException:
        raise HTTPException(
            status_code=401, detail='Неверный email или пароль'
        )
    if not user.is_admin:
        raise HTTPException(
            status_code=403, detail='Только админы могут получить токены!'
        )
    jwt_strategy = get_jwt_strategy()
    access_token = await jwt_strategy.write_token(user)
    refresh_token = create_refresh_token(user.id)
    return {'access_token': access_token, 'refresh_token': refresh_token}


@router.post('/jwt/refresh')
async def refresh_token(
    refresh_token: str, user_manager: UserManager = Depends(get_user_manager)
):
    """Кастомный эндпоинт для обновления токена.

    Параметры функции:
    1) refresh_token - токен для обновления access токена;
    2) user_manager - пользовательский менеджер.
    """
    user_id = verify_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=401, detail='Неверный или истёкший refresh-токен'
        )
    user = await user_manager.get(user_id)
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=403, detail='Только админы могут обновлять токены'
        )
    jwt_strategy = get_jwt_strategy()
    new_access_token = await jwt_strategy.write_token(user)
    return {'access_token': new_access_token}


@router.post('/jwt/logout')
async def logout(refresh_token: str) -> dict[str, str]:
    """Кастомный эндпоинт для выхода. Удаляет refresh_token.

    Параметры функции:
    1) refresh_token - токен для обновления access токена.
    """
    redis_client.delete(refresh_token)
    return {'message': 'Выход выполнен'}


# TODO: Удалить на релизе.
@router.get('/user/test/')
async def test_user_token(
    admin: User = Depends(current_admin_with_token),
) -> str:
    """Тестовый эндпоинт. Для проверки работы токена."""
    name = admin.name
    return f'Привет {name}. Лучший админ.'
