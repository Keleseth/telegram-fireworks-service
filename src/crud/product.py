from src.crud.base import CRUDBase
from src.database.alembic_models import Category

category_crud = CRUDBase(Category)
