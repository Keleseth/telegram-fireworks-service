from fastapi_users import FastAPIUsers

from src.api.auth.auth import auth_backend
from src.api.auth.manager import get_user_manager
from src.models.user import User
from src.schemas.user import UserCreate, UserRead, UserUpdate

fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backend],
    User,
    UserCreate,
    UserUpdate,
    UserRead,
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
