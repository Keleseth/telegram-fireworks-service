from fastapi import Request
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.exceptions import InvalidPasswordException
from fastapi_users.password import PasswordHelper
from sqladmin.authentication import (
    AuthenticationBackend as SQLAdminAuthBackend,
)

from src.api.auth.auth import (
    create_refresh_token,
    get_jwt_strategy,
    redis_client,
)
from src.api.auth.manager import UserManager
from src.database.db_dependencies import get_async_session


class SQLAdminAuth(SQLAdminAuthBackend):
    def __init__(
        self,
        secret_key: str,
        user_manager: UserManager,
        auth_backend: AuthenticationBackend,
    ) -> None:
        """Инициализация объекта."""
        super().__init__(secret_key)
        self.user_manager = user_manager
        self.auth_backend = auth_backend
        self.password_helper = PasswordHelper()

    async def login(self, request: Request) -> bool:
        # Извлекаем данные из формы
        # print(type(session))
        form = await request.form()
        email = form.get('username', 'ololo')
        password = form.get('password', 'ololo')
        print(type(email))
        print(password)

        if not email or not password:
            return False

        try:
            async for session in get_async_session():
                print(type(session))
                # Проверяем пользователя по email, передаём session
                print(email)
                user = await self.user_manager.get_by_email(
                    email, session=session
                )
                print('юзер по email получен')
                if user is None:
                    return False
                print(user.name)

                # Проверяем пароль против хеша
                if not user.hashed_password:
                    return False

                # Используем PasswordHelper для проверки пароля
                is_valid, _ = self.password_helper.verify_and_update(
                    password, user.hashed_password
                )
                if not is_valid:
                    return False

                # Проверяем, что пользователь — админ
                if not (user.is_admin or user.is_superuser):
                    return False

                # Для админов age_verified всегда True,
                # но на всякий случай проверим
                if not user.age_verified:
                    return False

                # Генерируем JWT-токен
                jwt_strategy = get_jwt_strategy()
                access_token = await jwt_strategy.write_token(user)

                # Генерируем refresh-токен и сохраняем в Redis
                refresh_token = create_refresh_token(user.id)

                # Сохраняем токены в сессии SQLAdmin
                request.session.update({
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user_id': str(user.id),
                })
            print('Господин жопосранчик')
            return True
        except InvalidPasswordException:
            return False
        except Exception as e:
            print(f'Ошибка при входе: {e}')
            return False

    async def logout(self, request: Request) -> bool:
        # Удаляем refresh-токен из Redis
        refresh_token = request.session.get('refresh_token')
        if refresh_token:
            redis_client.delete(refresh_token)

        # Очищаем сессию
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        # Проверяем наличие токена в сессии
        access_token = request.session.get('access_token')
        refresh_token = request.session.get('refresh_token')

        if not access_token or not refresh_token:
            return False

        try:
            # Проверяем refresh-токен в Redis
            user_id = redis_client.get(refresh_token)
            if not user_id:
                return False

            # Валидируем JWT-токен
            strategy = self.auth_backend.get_strategy()
            user = await strategy.read_token(access_token, self.user_manager)
            if user is None:
                return False

            # Проверяем, что пользователь — админ
            if not (user.is_admin or user.is_superuser):
                return False

            # Для админов age_verified всегда True
            if not user.age_verified:
                return False

            # Обновляем user_id в сессии
            request.session.update({'user_id': str(user.id)})
            return True
        except Exception:
            return False
