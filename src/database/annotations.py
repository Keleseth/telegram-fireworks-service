# Файл для повторяющихся аннотаций, например поля модели, такие как int
from datetime import datetime
from typing import Annotated

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import mapped_column

int_pk = Annotated[
    int,
    mapped_column(primary_key=True, unique=True)
]
not_null_and_unique = Annotated[
    str,
    mapped_column(unique=True, nullable=False)
]
created_at = Annotated[
    datetime,
    mapped_column(type_=TIMESTAMP(timezone=True), server_default=func.now()),
]
updated_at = Annotated[
    datetime,
    mapped_column(
        type_=TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=datetime.now,
    ),
]
