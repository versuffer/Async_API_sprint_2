from fastapi import APIRouter, Depends, status

from app.api.docs.tags import ApiTags
from app.schemas.v1.films_schemas import GetFilmSchemaOut
from app.schemas.v1.params_schema import SearchParams
from app.services.api.v1.films_service.films_service import FilmsService

search_router = APIRouter(prefix='/search')


@search_router.get(
    '',
    status_code=status.HTTP_200_OK,
    summary='Поиск фильмов',
    response_model=list[GetFilmSchemaOut],
    tags=[ApiTags.V1_FILMS],
)
async def search_films(
    params: SearchParams = Depends(),
    service: FilmsService = Depends(),
):
    return await service.search_films(**params.dict())
