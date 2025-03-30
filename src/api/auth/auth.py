import secrets
import uuid
from typing import Optional

import redis
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from src.api.auth.manager import get_user_manager
from src.config import settings
from src.models import User

# Подключение к Redis.
redis_client = redis.Redis(
    host=settings.redis_host,
    port=int(settings.redis_port),
    decode_responses=True,
)

# Настройка транспорта.
bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.secret, lifetime_seconds=300)


authentication_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager, [authentication_backend]
)


def create_refresh_token(user_id: uuid.UUID, lifetime_days: int = 7) -> str:
    """Создает refresh token в Redis."""
    token = secrets.token_hex(32)
    expires_in_seconds = lifetime_days * 24 * 60 * 60
    user_id_str = str(user_id)
    redis_client.setex(token, expires_in_seconds, user_id_str)
    return token


def verify_refresh_token(token: str) -> Optional[str]:
    """Проверка актуальности токена."""
    user_id: Optional[str] = redis_client.get(token)
    return user_id


user_admin_token = fastapi_users.current_user(active=True)
