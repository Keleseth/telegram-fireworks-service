from sqladmin import ModelView

from src.admin.constants import PAGE_SIZE
from src.models.media import Media


class MediaView(ModelView, model=Media):
    name = 'медиа'
    name_plural = 'Медиафайлы товаров'

    column_list = [Media.media_type, Media.media_url]
    form_excluded_columns = [
        'created_at',
        'updated_at',
    ]
    column_labels = {
        'media_url': 'url медиафайла',
    }

    page_size = PAGE_SIZE
