from uuid import UUID

from fastapi import Depends

from app.cruds.base import CrudInterface
from app.cruds.get_crud import get_crud
from app.schemas.v1.films_schemas import GetFilmExtendedSchemaOut, GetFilmSchemaOut
from app.schemas.v1.params_schema import FilmParams
from app.services.api.v1.base import BaseV1Service


class FilmsService(BaseV1Service):

    def __init__(self, crud: CrudInterface = Depends(get_crud)):
        self.crud = crud

    async def get_films(self, params: FilmParams) -> list[GetFilmSchemaOut] | None:
        return await self.crud.get_films(params)

    async def get_film(self, film_id: UUID) -> GetFilmExtendedSchemaOut | None:
        return await self.crud.get_film(film_id)

    async def search_films(self, page: int, page_size: int, query: str) -> list[GetFilmSchemaOut] | None:
        return await self.crud.search_films(page=page, page_size=page_size, query=query)
