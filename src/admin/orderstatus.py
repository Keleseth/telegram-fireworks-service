from sqladmin import ModelView

from src.models.order import OrderStatus


class OrderStatusView(ModelView, model=OrderStatus):
    """Представление акций в админке."""

    name = 'статус'
    name_plural = 'Статусы заказов'

    column_list = [OrderStatus.status_text]
    form_excluded_columns = [
        'created_at',
        'updated_at',
    ]
    column_details_exclude_list = [
        'id',
        'created_at',
        'updated_at',
    ]
    column_labels = {'status_text': 'текст статуса'}
