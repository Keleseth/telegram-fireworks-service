from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseJFModel

if TYPE_CHECKING:
    from src.models import Tag


class Newsletter(BaseJFModel):
    """Основная модель для рассылок.

    Поля:
        1. id: int - primary key.
        2. content: str - текст рассылки, информация о новостях и т.п.
        3. datetime_send: datetime - дата отправки.
        4. switch_send: bool - статус отправки.
        5. mediafiles: list['NewsletterMedia'] поле для связи.
           с моделью NewsletterMedia.
        6. age_verified: bool - поле фильтрации юзеров по совершеннолетию.
        7. canceled: bool - флаг, отменить ли рассылку.
        5. tags: list['Tag'] поле списка связанных объектов модели Tag.
    """

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    content: Mapped[str]
    number_of_orders: Mapped[int] = mapped_column(Integer, default=0)
    age_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    mediafiles: Mapped[list['NewsletterMedia']] = relationship(
        back_populates='newsletter',
        lazy='selectin',
    )
    tags: Mapped[list['Tag']] = relationship(
        'Tag',
        secondary='newslettertag',
        back_populates='newsletters',
        lazy='selectin',
    )
    datetime_send: Mapped[datetime]
    switch_send: Mapped[bool] = mapped_column(
        default=False,
        server_default=text('false'),
    )
    canceled: Mapped[bool] = mapped_column(Boolean, default=False)


class NewsletterMedia(BaseJFModel):
    """модель для медиа файлов рассылок.

    Поля:
        1. id: int - primary key.
        2. newsletter_id: int - рассылка, к которой относятся медифайлы.
        3. media_url: список ссылок на медиафайлы.
        4. newsletter: поле для связи с моделью Newsletter.
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
        lazy='selectin',
    )


class NewsletterTag(BaseJFModel):
    """Промежуточная модель many-to-many.

    Поля:
        1. tag_id: id тега.
        2. newsletter_id: id рассылки.

    Связывает между собой модели Tag и Newsletter.
    """

    tag_id: Mapped[int] = mapped_column(ForeignKey('tag.id'), primary_key=True)
    newsletter_id: Mapped[int] = mapped_column(
        ForeignKey('newsletter.id'), primary_key=True
    )
