from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import InvalidPasswordException, exceptions

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
from src.models import User
from src.schemas.user import AdminUserUpdate, UserCreate, UserRead, UserUpdate

router = APIRouter()


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
    schema: AdminUserUpdate,
    admin: User = Depends(current_admin),
    user_manager: UserManager = Depends(get_user_manager),
):
    """Обновить email и пароль админа через менеджер."""
    await user_manager.update(
        user_update=schema,
        user=admin,
        safe=True,
    )
    return await user_manager.update(
        user_update=schema,
        user=admin,
        safe=True,
    )


@router.patch(
    '/user/update-profile/',
    response_model=UserRead,
    summary='Обновление профиля пользователя через Telegram',
)
async def update_user_profile(
    schema: UserUpdate,
    telegram_user: User = Depends(current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    """Обновить профиль пользователя, включая адрес."""
    await user_manager.update(
        user_update=schema,
        user=telegram_user,
        safe=True,
    )
    return await user_manager.update(
        user_update=schema,
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
