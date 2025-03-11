from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database.annotations import int_pk
from src.models.base import BaseJFModel


class BotMessage(BaseJFModel):
    """Модель содеращая текст бота.

    Поля:
    id: int - primary key.
    message_text: язык текста.

    """

    id: Mapped[int_pk]
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    text_language: Mapped[str] = mapped_column(String, nullable=False)
    # TODO: продумать урпавлвения языкамми для пользователей,
    #  возможно создать отдельную таблицу языков с полями:
    #  id и language и ссылаться таблицами на неё.
