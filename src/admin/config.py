from fastapi import FastAPI
from sqladmin import Admin

from src.admin.category_admin import CategoryView
from src.admin.media_admin import MediaView
from src.admin.product_admin import FireworkView
from src.admin.promotion_admin import DiscountView
from src.admin.tag_admin import TagView
from src.admin.user_admin import UserView
from src.database.db_dependencies import engine


def setup_admin(app: FastAPI) -> Admin:
    """Настраивает админку и подключает её к FastAPI."""
    admin = Admin(app, engine, templates_dir='src/admin/templates')
    admin.add_view(FireworkView)
    admin.add_view(UserView)
    admin.add_view(TagView)
    admin.add_view(CategoryView)
    admin.add_view(DiscountView)
    admin.add_view(MediaView)
    return admin
