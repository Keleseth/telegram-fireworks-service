from sqladmin import ModelView

from src.admin.constants import PAGE_SIZE
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
        Newsletter.account_age,
        Newsletter.users_related_to_tag,
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
        'mediafiles': 'медиафайлы',
        'tags': 'теги',
        'content': 'контент рассылки',
        'number_of_orders': 'фильтр по кол-ву заказов',
        'age_verified': 'фильтр совершеннолетия',
        'datetime_send': 'дата отправки',
        'switch_send': 'отправлена',
        'canceled': 'отмена рассылки',
        'created_at': 'дата создания',
        'account_age': 'возраст аккаунта',
        'users_related_to_tag': 'тег для пользователя',
    }
    column_sortable_list = [
        'switch_send',
        'canceled',
        'datetime_send',
    ]
    column_formatters = generate_clickable_formatters(
        Newsletter, '/admin/newsletter/details', column_list
    )
    column_searchable_list = [
        'content',
    ]


class NewsletterMediaView(ModelView, model=NewsletterMedia):
    name = 'медиафайл рассылки'
    name_plural = 'Медиафайлы рассылок'

    column_list = [
        NewsletterMedia.media_url,
        NewsletterMedia.newsletters,
    ]
    form_excluded_columns = [
        'created_at',
        'updated_at',
    ]
    column_details_exclude_list = [
        'id',
        'created_at',
        'updated_at',
    ]
    column_labels = {
        'newsletters': 'рассылки',
        'media_url': 'ссылка на медиа',
    }

    page_size = PAGE_SIZE
