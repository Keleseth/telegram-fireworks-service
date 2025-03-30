from fastapi import Request
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.password import PasswordHelper
from sqladmin.authentication import (
    AuthenticationBackend as SQLAdminAuthBackend,
)

from src.api.auth.auth import (
    create_refresh_token,
    get_jwt_strategy,
    redis_client,
    verify_refresh_token,
)
from src.api.auth.manager import UserManager


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
        request.state.ok = True

        form = await request.form()
        email = form.get('username')
        password = form.get('password')

        if not email or not password:
            request.state.ok = False
            return False

        try:
            user = await self.user_manager.get_by_email(email)
        except Exception:
            request.state.ok = False
            return False

        if not user.hashed_password:
            request.state.ok = False
            return False

        is_valid, _ = self.password_helper.verify_and_update(
            password, user.hashed_password
        )
        if not is_valid:
            request.state.ok = False
            return False

        if not (user.is_admin or user.is_superuser):
            request.state.ok = False
            return False

        # if not user.age_verified:
        #     request.state.ok = False
        #     return False

        jwt_strategy = get_jwt_strategy()
        access_token = await jwt_strategy.write_token(user)
        refresh_token = create_refresh_token(user.id)

        request.session.update({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': str(user.id),
        })

        return True

    async def logout(self, request: Request) -> bool:
        # Удаляем refresh-токен из Redis
        refresh_token = request.session.get('refresh_token')
        print(refresh_token)
        if refresh_token:
            redis_client.delete(refresh_token)

        # Очищаем сессию
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        access_token = request.session.get('access_token')
        refresh_token = request.session.get('refresh_token')

        if not access_token or not refresh_token:
            return False

        try:
            user_id = verify_refresh_token(refresh_token)
            if not user_id:
                return False

            strategy = self.auth_backend.get_strategy()
            user = await strategy.read_token(access_token, self.user_manager)
            if user is None:
                user = await self.user_manager.get(user_id)
                if user is None:
                    return False

            if not (user.is_admin or user.is_superuser):
                return False
            jwt_strategy = get_jwt_strategy()
            new_access_token = await jwt_strategy.write_token(user)
            request.session.update({
                'access_token': new_access_token,
                'user_id': str(user.id),
            })
            return True
        except Exception:
            return False
