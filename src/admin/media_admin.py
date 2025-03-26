from sqladmin import ModelView

from src.models.media import Media


class MediaView(ModelView, model=Media):
    name = 'медиа'
    name_plural = 'Медиа'

    column_list = [Media.media_type, Media.media_url]
