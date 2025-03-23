# from typing import Any

# from sqladmin.filters import BaseSQLAlchemyFilter


# class PriceMinFilter(BaseSQLAlchemyFilter):
#     """Фильтр 'Цена от' (минимальное значение)."""

#     name = 'Диапазон цены "от"'  # То, что увидит админ в списке фильтров

#     def get_expression(self, model, field, value: Any):
#         """При вводе значения применяем фильтрацию field >= value.
#         Если значение не число, делаем фильтр ложным.
#         """
#         try:
#             value = float(value)
#         except ValueError:
#             return field == -1
#         return field >= value


# class PriceMaxFilter(BaseSQLAlchemyFilter):
#     """Фильтр 'Цена до' (максимальное значение)."""

#     name = 'Цена до'

#     def get_expression(self, model, field, value: Any):
#         """При вводе значения применяем фильтрацию field <= value.

#         Если значение не число, делаем фильтр ложным.
#         """
#         try:
#             value = float(value)
#         except ValueError:
#             return field == -1
#         return field <= value
