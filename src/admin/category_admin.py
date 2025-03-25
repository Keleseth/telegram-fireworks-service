from markupsafe import Markup
from sqladmin import ModelView

from src.admin.constants import PAGE_SIZE
from src.models.product import Category


class CategoryView(ModelView, model=Category):
    name = 'категория'
    name_plural = 'Категории'

    column_list = [Category.id, Category.name, Category.parent_category]
    column_details_list = [
        'id',
        'name',
        'created_at',
        'parent_category',
    ]
    form_excluded_columns = [
        'updated_at',
        'created_at',
    ]
    column_labels = {
        'id': 'ID',
        'name': 'название',
        'parent_category': 'Родительская категория',
        'created_at': 'дата создания',
        'updated_at': 'дата обновления',
    }
    column_sortable_list = ['name', 'id']
    column_default_sort = 'name'
    column_formatters = {
        'name': lambda m, _: Markup(
            '<a href="/admin/category/details/'
            f'{getattr(m, "id")}">{getattr(m, "name")}</a>'
        ),
    }

    page_size = PAGE_SIZE
    form_widget_args = {'fireworks': {'data-role': 'tagsinput'}}
