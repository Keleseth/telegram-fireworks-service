from sqladmin import ModelView

from src.admin.constants import PAGE_SIZE
from src.admin.utils import generate_clickable_formatters
from src.models.discounts import Discount


class DiscountView(ModelView, model=Discount):
    """Представление акций в админке."""

    name = 'акция'
    name_plural = 'Акции'

    column_list = [
        Discount.type,
        Discount.value,
        Discount.description,
        Discount.start_date,
        Discount.end_date,
        Discount.fireworks,
    ]
    form_excluded_columns = [
        'created_at',
        'updated_at',
    ]
    column_details_exclude_list = [
        'id',
        'hashed_password',
        'favorite_fireworks',
        'cart',
        'is_verified',
        'created_at',
        'updated_at',
    ]
    column_sortable_list = [
        'start_date',
        'end_date',
    ]
    column_labels = {
        'id': 'ID',
        'type': 'тип акции',
        'value': 'значение скидки',
        'start_date': 'дата и время начала акции',
        'end_date': 'дата и время окончания акции',
        'description': 'описание',
        'fireworks': 'товары акции',
    }
    column_searchable_list = ['type', 'value']
    column_formatters = generate_clickable_formatters(
        Discount, '/admin/newsletter/details', column_list
    )

    page_size = PAGE_SIZE
