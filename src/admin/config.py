from fastapi import FastAPI
from sqladmin import Admin

from src.admin.firework_media_admin import FireworkMediaAdmin
from src.admin.product_admin import FireworkAdmin
from src.admin.user_admin import UserAdmin
from src.database.db_dependencies import engine


def setup_admin(app: FastAPI) -> Admin:
    """Настраивает админку и подключает её к FastAPI."""
    admin = Admin(app, engine)
    admin.add_view(FireworkAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(FireworkMediaAdmin)
    return admin
