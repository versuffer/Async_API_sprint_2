from fastapi import APIRouter

from app.api.v1.films.films_router import films_router
from app.api.v1.genres.genres_router import genres_router
from app.api.v1.persons.persons_router import persons_router

v1_router = APIRouter(prefix='/v1')

v1_router.include_router(films_router)
v1_router.include_router(persons_router)
v1_router.include_router(genres_router)
