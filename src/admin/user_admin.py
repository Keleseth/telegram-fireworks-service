from markupsafe import Markup
from sqladmin import ModelView

# from sqladmin.filters import FilterEqual, FilterLike, FilterIn
from src.admin.constants import PAGE_SIZE
from src.models.user import User


class UserAdmin(ModelView, model=User):
    name = 'пользователь'
    name_plural = 'Пользователи'

    column_list = [
        User.telegram_id,
        User.name,
        User.email,
        User.is_admin,
        'has_orders',
    ]
    form_excluded_columns = [
        'cart',
        'updated_at',
        'exclude',
        'orders',
        'hashed_password',
        'favorite_fireworks',
    ]
    column_labels = {
        'telegram_id': 'telegram_id',
        'name': 'имя',
        'email': 'почта',
        'is_admin': 'администратор',
        'has_orders': 'кол-во заказов',
        'nickname': 'никнейм',
    }
    column_sortable_list = ['name', 'is_admin', 'has_orders']
    column_searchable_list = [
        'telegram_id',
        'name',
        'email',
    ]
    column_formatters = {
        'name': lambda user, _: Markup(
            '<a href="/admin/user/edit/'
            f'{getattr(user, "id")}">{getattr(user, "name")}</a>'
        ),
        'telegram_id': lambda user, _: Markup(
            '<a href="/admin/user/edit/'
            f'{getattr(user, "id")}">{getattr(user, "telegram_id")}</a>'
        ),
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
    }

    page_size = PAGE_SIZE
