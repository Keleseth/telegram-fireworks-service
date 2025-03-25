from sqladmin import ModelView

from src.models.discounts import Discount


class DiscountView(ModelView, model=Discount):
    """Представление акций в админке."""

    name = 'акция'
    name_plural = 'Акции'

    column_list = [
        Discount.id,
        Discount.type,
        Discount.value,
        Discount.description,
        Discount.start_date,
        Discount.end_date,
    ]

    form_excluded_columns = [
        'created_at',
        'updated_at',
    ]
