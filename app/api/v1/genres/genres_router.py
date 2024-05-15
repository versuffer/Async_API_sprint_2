from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache.decorator import cache

from app.api.docs.tags import ApiTags
from app.core.config import app_settings
from app.schemas.v1.genres_schemas import GenreSchemaOut
from app.schemas.v1.params_schema import DetailParams, ListParams
from app.services.api.v1.genres_service.genres_service import GenresService

genres_router = APIRouter(prefix='/genres')


@genres_router.get(
    '',
    status_code=status.HTTP_200_OK,
    summary='Получить список жанров',
    response_model=list[GenreSchemaOut],
    tags=[ApiTags.V1_GENRES],
)
@cache(expire=app_settings.DEFAULT_EXPIRE_TIME_SECONDS)
async def get_genres(
    query_params: ListParams = Depends(),
    service: GenresService = Depends(),
):
    if genres := await service.get_genres(query_params):
        return genres
    return []


@genres_router.get(
    '/{genre_id}',
    status_code=status.HTTP_200_OK,
    summary='Получить жанр по UUID',
    response_model=GenreSchemaOut,
    tags=[ApiTags.V1_GENRES],
)
@cache(expire=app_settings.DEFAULT_EXPIRE_TIME_SECONDS)
async def get_genre(
    query_params: DetailParams = Depends(),
    service: GenresService = Depends(),
):
    if genre := await service.get_genre(query_params.query):
        return genre
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
