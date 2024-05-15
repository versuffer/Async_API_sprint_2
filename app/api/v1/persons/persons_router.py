from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache

from app.api.docs.tags import ApiTags
from app.api.v1.persons.film.film_router import film_router
from app.api.v1.persons.search.search_router import search_router
from app.core.config import app_settings
from app.schemas.v1.params_schema import DetailParams
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
    query_params: DetailParams = Depends(),
    service: PersonsService = Depends(),
):
    return await service.get_person(query_params)
