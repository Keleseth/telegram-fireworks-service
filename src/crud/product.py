from src.crud.base import CRUDBaseRead
from src.models.product import Category, Firework

product_crud = CRUDBaseRead(Firework)
category_crud = CRUDBaseRead(Category)
