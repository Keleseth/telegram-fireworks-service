from markupsafe import Markup
from sqladmin import ModelView

from src.admin.constants import PAGE_SIZE
from src.models.product import Tag


class TagView(ModelView, model=Tag):
    name = 'тег'
    name_plural = 'Теги'

    column_list = [
        Tag.id,
        Tag.name,
    ]
    column_details_list = [
        'id',
        'name',
        'created_at',
        'fireworks',
    ]
    form_excluded_columns = [
        'updated_at',
        'created_at',
    ]
    column_labels = {
        'id': 'ID',
        'name': 'название',
        'fireworks': 'фейерверки тега',
        'created_at': 'дата создания',
        'updated_at': 'дата обновления',
    }
    column_sortable_list = ['name', 'id']
    column_default_sort = 'name'
    column_formatters = {
        'name': lambda m, _: Markup(
            '<a href="/admin/tag/details/'
            f'{getattr(m, "id")}">{getattr(m, "name")}</a>'
        ),
    }

    page_size = PAGE_SIZE
    form_widget_args = {'fireworks': {'data-role': 'tagsinput'}}
