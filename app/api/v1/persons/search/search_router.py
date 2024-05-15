from fastapi import APIRouter, Depends, status

from app.api.docs.tags import ApiTags
from app.schemas.v1.params_schema import SearchParams
from app.schemas.v1.persons_schemas import PersonSchemaOut
from app.services.api.v1.persons_service.persons_service import PersonsService

search_router = APIRouter(prefix='/search')


@search_router.get(
    '',
    status_code=status.HTTP_200_OK,
    summary='Поиск фильмов',
    response_model=list[PersonSchemaOut],
    tags=[ApiTags.V1_PERSONS],
)
async def search_persons(
    query_params: SearchParams = Depends(),
    service: PersonsService = Depends(),
):
    return await service.search_persons(query_params)
