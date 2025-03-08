from datetime import datetime

from sqlalchemy import ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseJFModel


class Newsletter(BaseJFModel):
    """Основная модель для рассылок.

    Поля:
        id: обычный айди.
        content: текст рассылки, информация о новостях и т.п.
        datetime_send: дата отправки.
        switch_send: статус отправки.
        mediafiles: поле для связи с моделью NewsletterMedia.
    """

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    content: Mapped[str]
    datetime_send: Mapped[datetime]
    switch_send: Mapped[bool] = mapped_column(
        default=False,
        server_default=text('false'),
    )
    mediafiles: Mapped['NewsletterMedia'] = relationship(
        back_populates='newsletter',
        lazy='joined',
    )


class NewsletterMedia(BaseJFModel):
    """модель для медиа файлов рассылок.

    Поля:
        id: обычный айди.
        newsletter_id: рассылка, к которой относятся медифайлы.
        media_url: список ссылок на медиафайлы.
        newsletter: поле для связи с моделью Newsletter.
    """

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    newsletter_id: Mapped[int] = mapped_column(ForeignKey('newsletter.id'))
    media_url: Mapped[str]
    newsletter: Mapped['Newsletter'] = relationship(
        back_populates='mediafiles',
        lazy='joined',
    )
