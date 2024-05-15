from uuid import UUID

from pydantic import BaseModel, Field


class GenreSchemaBase(BaseModel):
    id: UUID = Field(serialization_alias="uuid")
    name: str


class GenreSchema(GenreSchemaBase):
    description: str


class GenreSchemaOut(GenreSchema):
    pass
