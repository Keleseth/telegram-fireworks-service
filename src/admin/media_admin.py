from sqladmin import ModelView

from src.admin.constants import PAGE_SIZE
from src.admin.utils import generate_clickable_formatters
from src.models.media import Media


class MediaView(ModelView, model=Media):
    name = 'медиа'
    name_plural = 'Медиафайлы товаров'

    column_list = [
        Media.media_type,
        Media.media_url,
        Media.fireworks,
    ]
    form_excluded_columns = [
        'created_at',
        'updated_at',
        'formatted_media',
    ]
    column_labels = {
        'media_url': 'url медиафайла',
        'media_type': 'тип медиафайла',
        'fireworks': 'товары',
    }
    column_details_exclude_list = [
        'id',
        'created_at',
        'updated_at',
        'formatted_media',
    ]
    page_size = PAGE_SIZE

    column_formatters = generate_clickable_formatters(
        Media, '/admin/media/details', column_list
    )
