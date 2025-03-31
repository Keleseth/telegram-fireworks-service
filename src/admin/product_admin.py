from markupsafe import Markup
from sqladmin import ModelView
from sqlalchemy import select
from sqlalchemy.sql import Select
from starlette.requests import Request

# from starlette.responses import RedirectResponse
# from sqladmin.filters import FilterEqual, FilterLike, FilterIn
from src.admin.constants import PAGE_SIZE
from src.admin.utils import generate_clickable_formatters
from src.models.product import Category, Firework, Tag

# from sqladmin.filters import BooleanFilter, IntegerFilter

# def format_media(obj, name):
#     url = getattr(obj, name)
#     if not url:
#         return ''

#     return Markup(
#         f'<img src="{url}" style="max-width:100px; max-height:100px;">'
#     )


class FireworkView(ModelView, model=Firework):
    """Представление фейерверков в админке."""

    name = 'товар'
    name_plural = 'Товары'
    # list_template = 'sqladmin/custom_list.html'

    column_list = [
        Firework.code,
        Firework.article,
        Firework.name,
        Firework.category,
        Firework.tags,
        Firework.discounts,
        'favorited_count',
        'ordered_count',
        Firework.price,
    ]
    column_details_exclude_list = [
        'id',
        'favorited_by_users',
        'carts',
        'category_id',
        'updated_at',
        'order_fireworks',
    ]
    form_columns = [
        'code',
        'article',
        'name',
        'description',
        'category',
        'tags',
        'media',
        'properties',
        'discounts',
        'price',
        'measurement_unit',
        'charges_count',
        'effects_count',
        'product_size',
        'packing_material',
        'caliber',
    ]
    column_labels = {
        'id': 'ID',
        'name': 'название',
        'price': 'цена',
        'favorited_count': Markup(
            '<span title="Количество пользователей,'
            ' добавивших в избранное">избран</span>'
        ),
        'media': 'медиафайлы продукта',
        'category': 'категория',
        'tags': 'теги',
        'measurement_unit': 'единица измерения',
        'description': 'описание - как на рутуб',
        'article': 'артикул',
        'code': 'код',
        'discounts': 'акции фейерверка',
        'ordered_count': Markup(
            '<span title="Количество пользователей, заказавших'
            ' данный товар">Заказан</span>',
        ),
        'charges_count': 'количество зарядов',
        'effects_count': 'количество эффектов',
        'product_size': 'размер изделия',
        'packing_material': 'материал упаковки',
        'created_at': 'дата создания',
        'properties': 'доп. характеристики',
        'caliber': 'калибр',
    }
    column_sortable_list = [
        'name',
        'price',
        'favorited_count',
        'ordered_count',
    ]
    column_default_sort = 'name'
    column_searchable_list = ['name', 'article', 'code']
    # фильтрация объектов по полям включая relationship поля.
    column_filters_enabled = True
    writing_filters = {'Категория': 'category', 'Тег': 'tag'}
    column_formatters = generate_clickable_formatters(
        Firework, '/admin/newsletter/details', column_list
    )
    column_filters_enabled = True

    page_size = PAGE_SIZE

    # form_widget_args = {'tags': {'data-role': 'tagsinput'}}

    form_widget_args = {
        'tags': {
            'rows': 10,
            'style': 'min-height:200px; width:100%;',
        },
    }

    def list_query(self, request: Request) -> Select:
        stmt = select(Firework).distinct()

        category = request.query_params.get('category')
        if category:
            stmt = stmt.join(Firework.category).where(
                Category.name.ilike(f'%{category}%')
            )

        tag = request.query_params.get('tag')
        if tag:
            stmt = stmt.join(Firework.tags).where(Tag.name.ilike(f'%{tag}%'))

        return stmt
