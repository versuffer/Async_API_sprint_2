from enum import Enum


class ApiTags(Enum):
    V1_FILMS = 'API V1 / Films'
    V1_GENRES = 'API V1 / Genres'
    V1_PERSONS = 'API V1 / Persons'


# Теги отображаются в Swagger в порядке, заданном в списке
api_tags = [
    {
        'name': ApiTags.V1_FILMS,
    },
    {
        'name': ApiTags.V1_GENRES,
    },
    {
        'name': ApiTags.V1_PERSONS,
    },
]
