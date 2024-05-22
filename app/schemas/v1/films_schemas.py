from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class Roles(StrEnum):
    ACTOR = 'actor'
    WRITER = 'writer'
    DIRECTOR = 'director'


class GetFilmSchemaOut(BaseModel):
    id: UUID = Field(serialization_alias='uuid')
    title: str
    imdb_rating: float


class FilmGenre(BaseModel):
    id: UUID = Field(serialization_alias='uuid')
    name: str


class FilmPerson(BaseModel):
    id: UUID = Field(serialization_alias='uuid')
    full_name: str = Field(alias='name')


class FilmActor(FilmPerson):
    pass


class FilmWriter(FilmPerson):
    pass


class FilmDirector(FilmPerson):
    pass


class GetFilmExtendedSchemaOut(GetFilmSchemaOut):
    description: str
    genres: list[str]
    actors: list[FilmActor]
    writers: list[FilmWriter]
    directors: list[FilmDirector]

    def get_person_films(self, person_id: str) -> dict:
        """Метод используется для получения списков жанров конкретной персоны в ручке persons"""

        roles: list[Roles] = []

        roles.extend([Roles.ACTOR for actor in self.actors if str(actor.id) == str(person_id)])
        roles.extend([Roles.WRITER for writer in self.writers if str(writer.id) == str(person_id)])
        roles.extend([Roles.DIRECTOR for director in self.directors if str(director.id) == str(person_id)])

        return dict(uuid=self.id, roles=roles)
