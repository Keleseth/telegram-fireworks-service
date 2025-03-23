from sqladmin import ModelView

# from sqladmin.filters import FilterEqual, FilterLike, FilterIn
from src.models.user import User


class UserAdmin(ModelView, model=User):
    name = 'пользователь'
    name_plural = 'Пользователи'

    column_list = [User.telegram_id, User.name, User.email, User.is_admin]

    form_widget_args = {
        'is_admin': {
            'onchange': "if(this.checked && !confirm('Назначить пользователя"
            " администратором?')) { this.checked = false; }"
        }
    }
