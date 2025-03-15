from src.crud.base import CRUDBase, CRUDBaseRead
from src.models.product import Category, Firework

product_crud = CRUDBaseRead(Firework)
category_crud = CRUDBase(Category)
