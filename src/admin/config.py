from fastapi import FastAPI
from sqladmin import Admin

from src.admin.category_admin import CategoryView
from src.admin.product_admin import FireworkView
from src.admin.tag_admin import TagView
from src.admin.user_admin import UserView
from src.database.db_dependencies import engine


def setup_admin(app: FastAPI) -> Admin:
    """Настраивает админку и подключает её к FastAPI."""
    admin = Admin(app, engine)
    admin.add_view(FireworkView)
    admin.add_view(UserView)
    admin.add_view(TagView)
    admin.add_view(CategoryView)
    return admin
