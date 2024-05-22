from abc import ABC, abstractmethod
from uuid import UUID

from elasticsearch import Elasticsearch

from app.core.config import app_settings
from app.schemas.v1.films_schemas import GetFilmExtendedSchemaOut, GetFilmSchemaOut
from app.schemas.v1.genres_schemas import GenreSchema
from app.schemas.v1.params_schema import (
    DetailParams,
    FilmParams,
    ListParams,
    SearchParams,
)
from app.schemas.v1.persons_schemas import PersonSchema, PersonSchemaExtend


class FilmCrudInterface(ABC):
    @abstractmethod
    async def get_film(self, film_id: UUID) -> GetFilmExtendedSchemaOut | None:
        pass

    @abstractmethod
    async def search_films(self, query: str, page: int, page_size: int) -> list[GetFilmSchemaOut] | None:
        pass

    @abstractmethod
    async def get_films(self, params: FilmParams) -> list[GetFilmSchemaOut] | None:
        pass


class GenreCrudInterface(ABC):
    @abstractmethod
    async def get_genres(self, query_params: ListParams) -> list[GenreSchema] | None:
        pass

    @abstractmethod
    async def get_genre(self, genre_id: UUID) -> GenreSchema | None:
        pass


class PersonCrudInterface(ABC):
    @abstractmethod
    async def get_person(self, person_id: UUID) -> PersonSchema | None:
        pass

    @abstractmethod
    async def search_persons(self, query_params: SearchParams) -> list[PersonSchemaExtend] | None:
        pass

    @abstractmethod
    async def search_person_films(self, query_params: DetailParams) -> list[GetFilmExtendedSchemaOut] | None:
        pass


class BaseElasticCrud:
    def __init__(self):
        self.elastic = Elasticsearch(
            hosts=[app_settings.ELASTIC_URL],
            timeout=5,
        )

    def get(self, index: str, uuid: UUID):
        return self.elastic.get(index=index, id=str(uuid))

    def search(self, index: str, body: dict):
        return self.elastic.search(index=index, body=body)
