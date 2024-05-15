from typing import Literal
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class QueryMixin(BaseModel):
    query: str = Query()


class PaginationMixin(BaseModel):
    page: int = Query(default=1, gt=0)
    page_size: int = Query(default=10, gt=0, le=20)


class DetailParams(QueryMixin):
    query: UUID = Field(default=Query(), alias="id")


class SearchParams(PaginationMixin, QueryMixin):
    query: str = Field(default=Query(), alias="search_query")


class ListParams(PaginationMixin):
    pass


class FilmParams(PaginationMixin):
    sort: Literal['imdb_rating', '-imdb_rating'] | None = None
    genre: UUID | None = None
