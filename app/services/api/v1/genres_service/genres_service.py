from uuid import UUID

from fastapi import Depends

from app.cruds.base import GenreCrudInterface
from app.cruds.get_cruds import get_genre_crud
from app.schemas.v1.genres_schemas import GenreSchema
from app.services.api.v1.base import BaseV1Service


class GenresService(BaseV1Service):

    def __init__(self, crud: GenreCrudInterface = Depends(get_genre_crud)):
        self.crud = crud

    async def get_genres(self, query_params) -> list[GenreSchema] | None:
        return await self.crud.get_genres(query_params)

    async def get_genre(self, genre_id: UUID) -> GenreSchema | None:
        return await self.crud.get_genre(genre_id)
