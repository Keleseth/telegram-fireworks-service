from src.crud.base import CRUDBase
from src.models.product import Category, Firework
from src.schemas.product import (
    CategoryCreate,
    CategoryUpdate,
    FireworkCreate,
    FireworkUpdate,
)


class FireworkCRUD(CRUDBase[Firework, FireworkCreate, FireworkUpdate]):
    pass


class CategoryCRUD(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    pass


firework_crud = FireworkCRUD(Firework)
category_crud = CategoryCRUD(Category)
