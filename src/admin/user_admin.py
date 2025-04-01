from markupsafe import Markup
from sqladmin import ModelView
from sqlalchemy import select
from sqlalchemy.sql import Select
from starlette.requests import Request

from src.admin.constants import PAGE_SIZE
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
        'phone_number',
    ]
    column_details_exclude_list = [
        'id',
        'hashed_password',
        'favorite_fireworks',
        'cart',
        'is_verified',
    ]
    custom_filters = {
        'Активность': {
            'is_active:true': 'Активные',
            'is_active:false': 'Деактивированные',
        },
        'Роль': {
            'is_admin:true': 'Админы',
            'is_admin:false': 'Пользователи',
        },
    }
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
        'addresses': 'адреса',
        'birth_date': 'дата рождения',
    }
    column_filters_enabled = True
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

    def list_query(self, request: Request) -> Select:
        stmt = select(User)
        selected_filters = request.query_params.getlist('filters')

        for filter_str in selected_filters:
            if ':' not in filter_str:
                continue
            field, val = filter_str.split(':')
            val = val.lower()
            if field == 'is_admin':
                stmt = stmt.where(
                    User.is_admin.is_(val in {'true', '1', 'yes'})
                )
            elif field == 'is_active':
                stmt = stmt.where(
                    User.is_active.is_(val in {'true', '1', 'yes'})
                )

        return stmt
