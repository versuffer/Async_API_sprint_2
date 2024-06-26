from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache.decorator import cache

from app.api.docs.tags import ApiTags
from app.api.v1.persons.film.film_router import film_router
from app.api.v1.persons.search.search_router import search_router
from app.core.config import app_settings
from app.schemas.v1.persons_schemas import PersonSchemaOut
from app.services.api.v1.persons_service.persons_service import PersonsService

persons_router = APIRouter(prefix='/persons')
persons_router.include_router(search_router)
persons_router.include_router(film_router, prefix='/{person_id}')


@persons_router.get(
    '/{person_id}',
    status_code=status.HTTP_200_OK,
    summary='Получить участника фильма по UUID',
    response_model=PersonSchemaOut,
    tags=[ApiTags.V1_PERSONS],
)
@cache(expire=app_settings.DEFAULT_EXPIRE_TIME_SECONDS)
async def get_person(
    person_id: UUID,
    service: PersonsService = Depends(),
):
    if person := await service.get_person(person_id):
        return person
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
