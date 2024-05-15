from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class Roles(StrEnum):
    ACTOR = 'actor'
    WRITER = 'writer'
    DIRECTOR = 'director'


class PersonFilm(BaseModel):
    uuid: UUID
    roles: list[Roles]


class PersonSchema(BaseModel):
    id: UUID
    full_name: str


class PersonSchemaExtend(PersonSchema):
    films: list[PersonFilm]


class PersonSchemaOut(PersonSchemaExtend):
    id: UUID = Field(serialization_alias="uuid")
