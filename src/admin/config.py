from fastapi import FastAPI
from sqladmin import Admin

from src.admin.admin_dependencies import SQLAdminAuth
from src.admin.category_admin import CategoryView
from src.admin.media_admin import MediaView
from src.admin.newsletter_admin import NewsletterMediaView, NewsletterView
from src.admin.product_admin import FireworkView
from src.admin.product_extra_properties import (
    FireworkPropertyView,
    PropertyFieldView,
)
from src.admin.promotion_admin import DiscountView
from src.admin.tag_admin import TagView
from src.admin.upload_admin import AdminUploadCSVView
from src.admin.user_admin import UserView
from src.api.auth.auth import authentication_backend
from src.api.auth.manager import get_user_manager_no_depends
from src.config import settings
from src.database.db_dependencies import engine

# secret_key = os.getenv('ADMIN_SECRET_KEY', 'default_insecure_key_for_dev')


async def get_sqladmin_auth():
    user_manager = await anext(get_user_manager_no_depends())
    return SQLAdminAuth(
        secret_key=settings.secret,
        user_manager=user_manager,
        auth_backend=authentication_backend,
    )


async def setup_admin(app: FastAPI) -> Admin:
    """Настраивает админку и подключает её к FastAPI."""
    admin = Admin(
        app,
        engine,
        authentication_backend=await get_sqladmin_auth(),
        templates_dir='src/admin/templates',
    )
    admin.add_view(UserView)
    admin.add_view(FireworkView)
    admin.add_view(PropertyFieldView)
    admin.add_view(FireworkPropertyView)
    admin.add_view(CategoryView)
    admin.add_view(TagView)
    admin.add_view(DiscountView)
    admin.add_view(MediaView)
    admin.add_view(NewsletterView)
    admin.add_view(NewsletterMediaView)
    admin.add_view(AdminUploadCSVView)
    return admin
