from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database.annotations import int_pk
from src.models.base import BaseJFModel


class BotInfo(BaseJFModel):
    """Модель содержащая информацию о боте, компании и контактах."""

    id: Mapped[int_pk]
    bot_info: Mapped[str] = mapped_column(Text)
    about_company: Mapped[str] = mapped_column(Text)
    contacts: Mapped[str] = mapped_column(Text)
