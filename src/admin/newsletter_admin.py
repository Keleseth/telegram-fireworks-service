from sqladmin import ModelView

from src.admin.utils import generate_clickable_formatters
from src.models.newsletter import Newsletter, NewsletterMedia


class NewsletterView(ModelView, model=Newsletter):
    name = 'рассылка'
    name_plural = 'Рассылки'

    column_list = [
        Newsletter.content,
        Newsletter.tags,
        Newsletter.mediafiles,
        Newsletter.datetime_send,
        Newsletter.number_of_orders,
        Newsletter.age_verified,
        Newsletter.switch_send,
        Newsletter.canceled,
    ]
    form_excluded_columns = [
        'created_at',
        'updated_at',
        'switch_send',
    ]
    column_details_exclude_list = [
        'id',
        'updated_at',
    ]
    column_labels = {
        'mediafiles': 'медиафайлы рассылки',
        'tags': 'теги рассылки',
        'content': 'контент рассылки',
        'number_of_orders': 'фильтр по кол-ву заказов',
        'age_verified': 'фильтр совершеннолетия',
        'datetime_send': 'дата отправки',
        'switch_send': 'отправлена',
        'canceled': 'отмена рассылки',
        'created_at': 'дата создания',
    }
    column_sortable_list = [
        'switch_send',
        'canceled',
        'datetime_send',
    ]
    column_formatters = generate_clickable_formatters(
        Newsletter, '/admin/newsletter/details', column_list
    )


class NewsletterMediaView(ModelView, model=NewsletterMedia):
    name = 'медиа рассылки'
    name_plural = 'Медиа рассылок'

    column_exclude_list = [
        NewsletterMedia.id,
        NewsletterMedia.created_at,
        NewsletterMedia.updated_at,
    ]
    form_excluded_columns = [
        'created_at',
        'updated_at',
    ]
    column_details_exclude_list = [
        'id',
        'updated_at',
    ]
    column_labels = {
        'newsletters': 'связанные рассылки',
        'media_url': 'ссылка на медиа',
    }
