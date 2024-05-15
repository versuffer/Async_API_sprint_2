from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache.decorator import cache

from app.api.docs.tags import ApiTags
from app.api.v1.films.search.search_router import search_router
from app.core.config import app_settings
from app.schemas.v1.films_schemas import GetFilmExtendedSchemaOut, GetFilmSchemaOut
from app.schemas.v1.params_schema import FilmParams
from app.services.api.v1.films_service.films_service import FilmsService

films_router = APIRouter(prefix='/films')
films_router.include_router(search_router)


@films_router.get(
    '',
    status_code=status.HTTP_200_OK,
    summary='Получить список фильмов',
    response_model=list[GetFilmSchemaOut],
    tags=[ApiTags.V1_FILMS],
)
@cache(expire=app_settings.DEFAULT_EXPIRE_TIME_SECONDS)
async def get_films(
    params: FilmParams = Depends(),
    service: FilmsService = Depends(),
):
    return await service.get_films(params)


@films_router.get(
    '/{film_id}',
    status_code=status.HTTP_200_OK,
    summary='Получить фильм по UUID',
    response_model=GetFilmExtendedSchemaOut,
    tags=[ApiTags.V1_FILMS],
)
@cache(expire=app_settings.DEFAULT_EXPIRE_TIME_SECONDS)
async def get_film(
    film_id: UUID,
    service: FilmsService = Depends(),
):
    if film := await service.get_film(film_id):
        return film
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
