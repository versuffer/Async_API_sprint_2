from enum import StrEnum

from pydantic import BaseModel, Field

from app.core.logs import logger
from app.schemas.v1.films_schemas import GetFilmExtendedSchemaOut
from app.schemas.v1.genres_schemas import GenreSchema
from app.schemas.v1.persons_schemas import PersonSchema


class ElasticFilmSeachResponse(BaseModel):
    films: dict = Field(alias='hits')

    @property
    def films_list(self) -> list[GetFilmExtendedSchemaOut]:
        return [GetFilmExtendedSchemaOut(**film["_source"]) for film in self.films["hits"]]


class ElasticGetFilmResponse(BaseModel):
    film: GetFilmExtendedSchemaOut = Field(alias='_source')


class IndexList(StrEnum):
    MOVIES = "movies"
    GENRES = "genres"
    PERSONS = "persons"


class BaseObject(BaseModel):
    index: IndexList = Field(alias="_index")
    id: str = Field(alias="_id")
    source: dict = Field(alias="_source", exclude=True)

    @property
    def get_out_schema_source(self):
        match self.index:
            case IndexList.GENRES:
                return GenreSchema(**self.source)
            case IndexList.MOVIES:
                return GetFilmExtendedSchemaOut(**self.source)
            case IndexList.PERSONS:
                return PersonSchema(**self.source)
            case _:
                logger.error("Ops not match index: %s", self.index)


class Object(BaseObject):
    score: float = Field(alias="_score")


class Result(BaseModel):
    total: dict
    objects: list[Object] = Field(alias="hits", exclude=True)


class ElasticSearchResponse(BaseModel):
    result: Result = Field(alias="hits")

    @property
    def get_objects(self):
        return [obj.get_out_schema_source for obj in self.result.objects]

    @property
    def get_object(self):
        result = [obj.get_out_schema_source for obj in self.result.objects]
        return result[0] if result else None

    @property
    def uuid_list(self):
        return [obj.id for obj in self.result.objects]


class ElasticGetResponse(BaseObject):
    pass
