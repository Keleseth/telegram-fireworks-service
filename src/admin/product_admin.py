from markupsafe import Markup
from sqladmin import ModelView

# from sqladmin.filters import FilterEqual, FilterLike, FilterIn
from src.admin.constants import PAGE_SIZE
from src.models.product import Firework


class FireworkAdmin(ModelView, model=Firework):
    """Представление фейерверков в админке."""

    name = 'Фейерверк'
    name_plural = 'Фейерверки'

    column_list = [
        Firework.id,
        Firework.name,
        'favorited_count',
        'ordered_count',
        Firework.price,
        Firework.category,
        Firework.tags,
        Firework.article,
        Firework.code,
        Firework.discounts,
        Firework.media,
    ]
    form_excluded_columns = [
        'carts',
        'favorited_by_users',
        'created_at',
        'updated_at',
    ]
    column_searchable_list = ['name', 'article', 'code']
    column_sortable_list = [
        'id',
        'name',
        'price',
        'favorited_count',
        'ordered_count',
    ]

    # фильтрация объектов по полям включая relationship поля.
    column_filters = [
        Firework.name,
        Firework.category,
        Firework.price,
        Firework.tags,
    ]
    column_default_sort = 'id'
    column_labels = {
        'id': 'ID',
        'name': 'Название',
        'price': 'Цена',
        'favorited_count': Markup(
            '<span title="Количество пользователей,'
            ' добавивших в избранное">Избран</span>'
        ),
        'category': 'Категория',
        'tags': 'Теги',
        'article': 'Артикул',
        'code': 'Код',
        'discounts': 'Акции фейерверка',
        'ordered_count': Markup(
            '<span title="Количество пользователей, заказавших'
            ' данный товар">Заказан</span>',
        ),
    }
    column_formatters = {
        'name': lambda m, _: Markup(
            '<a href="/admin/firework/edit/'
            f'{getattr(m, "id")}">{getattr(m, "name")}</a>'
        ),
    }
    column_filters_enabled = True

    page_size = PAGE_SIZE

    form_widget_args = {'tags': {'data-role': 'tagsinput'}}
