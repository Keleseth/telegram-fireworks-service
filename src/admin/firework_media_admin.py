from sqladmin import ModelView

from src.admin.constants import PAGE_SIZE
from src.models.media import FireworkMedia


class FireworkMediaAdmin(ModelView, model=FireworkMedia):
    """Представление фейерверков в админке."""

    name = 'Медиа для Фейерверка'
    name_plural = 'Медиа для Фейерверков'

    column_list = [
        FireworkMedia.firework_id,
        FireworkMedia.image_id,
    ]

    form_excluded_columns = [
        'carts',
        'favorited_by_users',
        'created_at',
        'updated_at',
    ]

    page_size = PAGE_SIZE
