from uuid import UUID

from fastapi import Depends

from app.cruds.base import PersonCrudInterface
from app.cruds.get_cruds import get_person_crud
from app.schemas.v1.params_schema import DetailParams, SearchParams
from app.schemas.v1.persons_schemas import PersonSchema
from app.services.api.v1.base import BaseV1Service


class PersonsService(BaseV1Service):

    def __init__(self, crud: PersonCrudInterface = Depends(get_person_crud)):
        self.crud = crud

    async def get_person(self, person_id: UUID) -> PersonSchema | None:
        return await self.crud.get_person(person_id)

    async def get_person_films(self, query_params: DetailParams):
        return await self.crud.search_person_films(query_params)

    async def search_persons(self, query_params: SearchParams):
        return await self.crud.search_persons(query_params)
