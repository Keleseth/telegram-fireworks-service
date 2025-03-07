from typing import List

from sqlalchemy import DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from database import BaseJFModel


class Newsletter(BaseJFModel):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True,
    )
    content: Mapped[Text]
    datetime_send: Mapped[DateTime]
    switch_send: Mapped[bool] = mapped_column(
        default=False, server_default=text("'false'"),
        )


class NewsletterMedia(BaseJFModel):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True,
    )
    newsletter_id: Mapped[int] = mapped_column(ForeignKey('newsletter.id'))
    media_url: Mapped[List[str]]
