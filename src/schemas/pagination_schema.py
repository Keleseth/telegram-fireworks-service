from pydantic import BaseModel

PAGINATION_LIMIT = 10
PAGINATION_OFFSET = 0
MIN_PAGINATION_OFFSET = 0
MIN_PAGINATION_LIMIT = 1
MAX_PAGINATION_LIMIT = 10


class PaginationSchema(BaseModel):
    offset: int = PAGINATION_OFFSET
    limit: int = PAGINATION_LIMIT
