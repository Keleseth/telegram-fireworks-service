# from sqladmin import ModelView


# class BaseAdminView(ModelView):
#     column_list = []

#     def _universal_formatter(self, obj, value):
#         if value is None:
#             return 'пусто'
#         if isinstance(value, bool):
#             return 'да' if value else 'нет'
#         return value

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         if not hasattr(
#             self, 'column_formatters'
#         ) or self.column_formatters is None:
#             self.column_formatters = {}

#         for col in self.column_list:
#             if col.key not in self.column_formatters:
#                 self.column_formatters[
#                     col.key
#                 ] = self._universal_formatter
