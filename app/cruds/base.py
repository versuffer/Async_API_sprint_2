from abc import ABC, abstractmethod
from uuid import UUID

from app.schemas.v1.films_schemas import GetFilmExtendedSchemaOut, GetFilmSchemaOut
from app.schemas.v1.genres_schemas import GenreSchema
from app.schemas.v1.params_schema import (
    DetailParams,
    FilmParams,
    ListParams,
    SearchParams,
)
from app.schemas.v1.persons_schemas import PersonSchema, PersonSchemaExtend


class CrudInterface(ABC):
    @abstractmethod
    async def get_film(self, film_id: UUID) -> GetFilmExtendedSchemaOut | None:
        pass

    @abstractmethod
    async def search_films(self, query: str, page: int, page_size: int) -> list[GetFilmSchemaOut] | None:
        pass

    @abstractmethod
    async def get_films(self, params: FilmParams) -> list[GetFilmSchemaOut] | None:
        pass

    @abstractmethod
    async def get_genres(self, query_params: ListParams) -> list[GenreSchema] | None:
        pass

    @abstractmethod
    async def get_genre(self, genre_id: UUID) -> GenreSchema | None:
        pass

    @abstractmethod
    async def get_person(self, person_id: UUID) -> PersonSchema | None:
        pass

    @abstractmethod
    async def search_persons(self, query_params: SearchParams) -> list[PersonSchemaExtend] | None:
        pass

    @abstractmethod
    async def search_person_films(self, query_params: DetailParams) -> list[GetFilmExtendedSchemaOut] | None:
        pass
