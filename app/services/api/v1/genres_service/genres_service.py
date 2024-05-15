from uuid import UUID

from fastapi import Depends

from app.cruds.elastic import ElasticCrud
from app.schemas.v1.genres_schemas import GenreSchema
from app.services.api.v1.base import BaseV1Service


class GenresService(BaseV1Service):

    def __init__(self, crud: ElasticCrud = Depends()):
        self.crud = crud

    async def get_genres(self, query_params) -> list[GenreSchema]:
        return await self.crud.get_genres(query_params)

    async def get_genre(self, genre_id: UUID) -> GenreSchema:
        return await self.crud.get_genre(genre_id)
