from markupsafe import Markup
from sqladmin import ModelView

# from starlette.responses import RedirectResponse
# from sqladmin.filters import FilterEqual, FilterLike, FilterIn
from src.admin.constants import PAGE_SIZE
from src.admin.utils import generate_clickable_formatters
from src.models.product import Firework

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
        'favorited_by_users',
        'carts',
        'category_id',
        'updated_at',
        'order_fireworks',
    ]
    form_excluded_columns = [
        'id',
        'carts',
        'favorited_by_users',
        'created_at',
        'updated_at',
        'order_fireworks',
        'properties',
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
    # column_formatters = {
    #     'name': lambda m, _: Markup(
    #         '<a href="/admin/firework/details/'
    #         f'{getattr(m, "id")}">{getattr(m, "name")}</a>'
    #     ),
    #     'code': lambda m, _: Markup(
    #         '<a href="/admin/firework/details/'
    #         f'{getattr(m, "id")}">{getattr(m, "code")}</a>'
    #     ),
    #     'article': lambda m, _: Markup(
    #         '<a href="/admin/firework/details/'
    #         f'{getattr(m, "id")}">{getattr(m, "article")}</a>'
    #     ),
    #     'created_at': format_date,
    #     # 'media': format_media,
    # }
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
