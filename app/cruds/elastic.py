from uuid import UUID

import elasticsearch
from elasticsearch import Elasticsearch
from pydantic import ValidationError

from app.core.config import es_settings
from app.core.logs import logger
from app.cruds.base import CrudInterface
from app.schemas.elastic_responses import (
    ElasticFilmSeachResponse,
    ElasticGetFilmResponse,
    ElasticGetResponse,
    ElasticSearchResponse,
)
from app.schemas.v1.films_schemas import GetFilmExtendedSchemaOut, GetFilmSchemaOut
from app.schemas.v1.genres_schemas import GenreSchema, GenreSchemaBase
from app.schemas.v1.params_schema import DetailParams, FilmParams, ListParams
from app.schemas.v1.persons_schemas import PersonSchema, PersonSchemaExtend


class ElasticCrud(CrudInterface):
    def __init__(self):
        self.elastic = Elasticsearch([es_settings.dict()], timeout=5)

    @staticmethod
    async def build_film_search_body(
        query: str | None, page: int, page_size: int, sort: str | None, genre: UUID | None
    ):
        # основной шаблон запроса с использованием match_all, если других деталей нет
        body: dict = {
            "query": {"bool": {"must": [{"match_all": {}}], "filter": []}},
            "size": page_size,
            "from": (page - 1) * page_size,
        }

        if query:
            body["query"]["bool"]["must"].append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["title", "description", "directors_names", "actors_names", "writers_names"],
                    }
                }
            )

        if genre:
            body["query"]["bool"]["filter"].append({"term": {"genres": genre}})

        if sort:
            direction = "desc" if sort.startswith('-') else "asc"
            field_name = sort.lstrip('-')
            body["sort"] = [{field_name: {"order": direction}}]

        return body

    async def get_film(self, film_id: UUID) -> GetFilmExtendedSchemaOut | None:
        try:
            result = self.elastic.get(index="movies", id=str(film_id))
            parsed_result = ElasticGetFilmResponse(**result)
            film = parsed_result.film
            film_genres = []
            for genre in film.genres:
                body: dict = {
                    "query": {"match": {"name": {"query": genre, "fuzziness": "auto"}}},
                }
                genre_result = self.elastic.search(index="genres", body=body)
                validated_genre = ElasticSearchResponse(**genre_result.body).get_object
                if validated_genre:
                    film_genres.append(GenreSchemaBase(**validated_genre.dict()))
            film.genres = film_genres  # type: ignore
            return film
        except elasticsearch.NotFoundError as error:
            logger.warning("Не найден фильм с id: %s, ошибка: %s", film_id, error)
            return None
        except ValidationError as error:
            logger.error("Ошибка валидации: %s", error)
            return None
        except Exception as error:
            logger.error("Неизвестная ошибка при получении фильма с id: %s, ошибка: %s", film_id, error)
            return None

    async def search_films(self, query: str, page: int, page_size: int) -> list[GetFilmSchemaOut]:
        try:
            body = await self.build_film_search_body(query, page, page_size, None, None)
            results = self.elastic.search(index="movies", body=body)
            parsed_results = ElasticFilmSeachResponse(**results)
            return parsed_results.films_list  # type:ignore
        except Exception as error:
            logger.error("Неизвестная ошибка при получении фильмов по запросу: %s, ошибка: %s", query, error)
            return []

    async def get_films(self, params: FilmParams) -> list[GetFilmSchemaOut]:
        try:
            if params and params.genre:
                genre = await self.get_genre(params.genre)
                body = await self.build_film_search_body(
                    query=None, **params.dict() | {'genre': genre.name}  # type: ignore
                )
            else:
                body = await self.build_film_search_body(query=None, **params.dict())  # type: ignore
            results = self.elastic.search(index="movies", body=body)
            parsed_results = ElasticFilmSeachResponse(**results)
            return parsed_results.films_list  # type:ignore
        except Exception as error:
            logger.error("Неизвестная ошибка при получении фильмов: %s", error)
            return []

    async def get_genres(self, query_params: ListParams) -> list[GenreSchema] | None:
        try:
            result = self.elastic.search(
                index="genres", size=query_params.page_size, from_=(query_params.page - 1) * query_params.page_size
            )
            validated_obj = ElasticSearchResponse(**result.body)
            return validated_obj.get_objects
        except ValidationError as error:
            logger.error("Ошибка валидации: %s", error)
            return None
        except Exception as error:
            logger.error("Неизвестная ошибка при получении всех жанров: %s", error)
            return None

    async def get_genre(self, genre_id: UUID) -> GenreSchema | None:
        try:
            result = self.elastic.get(index="genres", id=str(genre_id))
            validated_obj = ElasticGetResponse(**result.body)
            return validated_obj.get_out_schema_source
        except elasticsearch.NotFoundError as error:
            logger.warning("Не найден жанр: %s", error)
            return None
        except ValidationError as error:
            logger.error("Ошибка валидации: %s", error)
            return None
        except Exception as error:
            logger.error("Неизвестная ошибка при получении жанра: %s", error)
            return None

    async def get_person(self, person_id: UUID) -> PersonSchema | None:
        try:
            person = self.elastic.get(index="persons", id=str(person_id))
            validated_person = ElasticGetResponse(**person.body)

            person_movies = self.elastic.search(index="movies", body=self.person_films_body(validated_person.id))
            validated_movies = ElasticSearchResponse(**person_movies.body)

            films = [movie.get_person_films(validated_person.id) for movie in validated_movies.get_objects]
            return PersonSchemaExtend(**dict(validated_person.get_out_schema_source.model_dump(), films=films))
        except elasticsearch.NotFoundError as error:
            logger.warning("Не найдено действующее лицо: %s", error)
            return None
        except ValidationError as error:
            logger.error("Ошибка валидации: %s", error)
            return None
        except Exception as error:
            logger.error("Неизвестная ошибка при получении действующего лица: %s", error)
            return None

    async def search_persons(self, query_params) -> list[PersonSchemaExtend] | None:

        body: dict = {
            "size": query_params.page_size,
            "from": (query_params.page - 1) * query_params.page_size,
            "query": {"match": {"full_name": {"query": query_params.query, "fuzziness": "auto"}}},
        }

        try:
            persons_result = self.elastic.search(index="persons", body=body)
            persons = ElasticSearchResponse(**persons_result.body)

            result: list[PersonSchemaExtend] = []

            for person in persons.get_objects:
                movies_result = self.elastic.search(index="movies", body=self.person_films_body(person.id))
                validated_movies = ElasticSearchResponse(**movies_result.body)

                films = [movie.get_person_films(person.id) for movie in validated_movies.get_objects]

                person_movies = PersonSchemaExtend(**person.model_dump() | {"films": films})

                result.append(person_movies)

            return result

        except elasticsearch.NotFoundError as error:
            logger.warning("Не найдено действующее лицо: %s", error)
            return None
        except ValidationError as error:
            logger.error("Ошибка валидации: %s", error)
            return None
        except Exception as error:
            logger.error("Неизвестная ошибка при получении действующего лица: %s", error)
            return None

    async def search_person_films(self, query_params: DetailParams) -> list[GetFilmExtendedSchemaOut] | None:

        try:
            movies_result = self.elastic.search(index="movies", body=self.person_films_body(query_params.query))
            validated_movies = ElasticSearchResponse(**movies_result.body)
            return validated_movies.get_objects

        except elasticsearch.NotFoundError as error:
            logger.warning("Не найдено действующее лицо: %s", error)
            return None
        except ValidationError as error:
            logger.error("Ошибка валидации: %s", error)
            return None
        except Exception as error:
            logger.error("Неизвестная ошибка при получении действующего лица: %s", error)
            return None

    @staticmethod
    def person_films_body(uuid) -> dict:
        return {
            "query": {
                "bool": {
                    "should": [
                        {"nested": {"path": "actors", "query": {"bool": {"must": [{"match": {"actors.id": uuid}}]}}}},
                        {"nested": {"path": "writers", "query": {"bool": {"must": [{"match": {"writers.id": uuid}}]}}}},
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"bool": {"must": [{"match": {"directors.id": uuid}}]}},
                            }
                        },
                    ]
                }
            }
        }
