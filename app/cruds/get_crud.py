from app.cruds.base import CrudInterface
from app.cruds.elastic import ElasticCrud


def get_crud() -> CrudInterface:
    return ElasticCrud()
