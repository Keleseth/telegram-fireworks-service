from markupsafe import Markup
from sqladmin import ModelView

# from sqladmin.filters import FilterEqual, FilterLike, FilterIn
from src.admin.constants import PAGE_SIZE
from src.admin.utils import format_date
from src.models.user import User


class UserView(ModelView, model=User):
    name = 'пользователь'
    name_plural = 'Пользователи'

    column_list = [
        User.telegram_id,
        User.name,
        User.email,
        'has_orders',
        User.created_at,
    ]
    form_excluded_columns = [
        'cart',
        'updated_at',
        'exclude',
        'orders',
        'hashed_password',
        'favorite_fireworks',
        'addresses',
        'age_verified',
        'created_at',
        'is_verified',
    ]
    column_details_exclude_list = [
        'hashed_password',
        'favorite_fireworks',
    ]
    column_labels = {
        'telegram_id': 'telegram_id',
        'name': 'имя',
        'email': 'почта',
        'is_admin': 'администратор',
        'has_orders': 'кол-во заказов',
        'orders': 'заказы',
        'nickname': 'никнейм',
        'is_active': 'активен',
        'created_at': 'дата создания',
        # 'favorited_count': Markup(
        #     '<span title="Количество пользователей,'
        #     ' добавивших в избранное">Избран</span>'
        # ),
        'phone_number': 'телефонный номер',
        'age_verified': 'подтверждение совершеннолетия',
        'is_superuser': 'суперпользователь',
        'id': 'ID',
        'updated_at': 'дата изменения',
    }
    column_sortable_list = ['name', 'is_admin', 'has_orders', 'created_at']
    column_default_sort = 'name'
    column_searchable_list = [
        'telegram_id',
        'name',
        'email',
    ]
    column_formatters = {
        'name': lambda user, _: Markup(
            '<a href="/admin/user/details/'
            f'{getattr(user, "id")}">{getattr(user, "name")}</a>'
        ),
        'telegram_id': lambda user, _: Markup(
            '<a href="/admin/user/details/'
            f'{getattr(user, "id")}">{getattr(user, "telegram_id")}</a>'
        ),
        'created_at': format_date,
    }
    form_widget_args = {
        'is_admin': {
            'onchange': "if(this.checked && !confirm('Назначить пользователя"
            " администратором?')) { this.checked = false; }"
        },
        'is_superuser': {
            'onchange': "if(this.checked && !confirm('Назначить пользователя"
            " суперюзером?')) { this.checked = false; }"
        },
        'created_at': {'readonly': True},
        'is_active': {
            'title': 'Если выключено — пользователь не сможет '
            'взаимодействовать с ботом.',
        },
    }

    page_size = PAGE_SIZE
