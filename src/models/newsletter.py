from typing import List

from database import Base
from sqlalchemy import DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column


class Newsletter(Base):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True,
    )
    content: Mapped[Text]
    datetime_send: Mapped[DateTime]
    switch_send: Mapped[bool] = mapped_column(
        default=False, server_default=text("'false'"),
        )


class NewsletterMedia(Base):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True,
    )
    newsletter_id: Mapped[int] = mapped_column(ForeignKey('newsletters.id'))
    media_url: Mapped[List[str]]
