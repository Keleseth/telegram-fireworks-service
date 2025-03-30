from markupsafe import Markup
from sqladmin import ModelView

from src.admin.constants import PAGE_SIZE
from src.models.product import Category


class CategoryView(ModelView, model=Category):
    name = 'категория товара'
    name_plural = 'Категории товаров'

    column_list = [
        Category.id,
        Category.name,
        Category.parent_category,
        Category.fireworks,
    ]
    column_details_list = [
        'name',
        'parent_category',
        'categories',
        'created_at',
    ]
    form_excluded_columns = [
        'updated_at',
        'created_at',
    ]
    column_labels = {
        'id': 'ID',
        'name': 'название',
        'parent_category': 'родительская категория',
        'created_at': 'дата создания',
        'updated_at': 'дата обновления',
        'categories': 'подкатегории',
        'fireworks': 'связанные фейерверки',
    }
    column_sortable_list = ['name', 'id']
    column_default_sort = 'name'
    column_searchable_list = ['name']
    column_formatters = {
        'name': lambda m, _: Markup(
            '<a href="/admin/category/details/'
            f'{getattr(m, "id")}">{getattr(m, "name")}</a>'
        ),
    }

    page_size = PAGE_SIZE
    form_widget_args = {'fireworks': {'data-role': 'tagsinput'}}
