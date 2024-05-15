from contextlib import asynccontextmanager
from pprint import pformat

import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from app.api.api_router import api_router
from app.api.docs.tags import api_tags
from app.core.config import app_settings
from app.core.logs import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(str(app_settings.REDIS_DSN))
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(
    title=app_settings.APP_TITLE,
    description=app_settings.APP_DESCRIPTION,
    version='1.0.0',
    debug=app_settings.DEBUG,
    docs_url='/',
    openapi_tags=api_tags,
    lifespan=lifespan,
)

app.include_router(api_router)


if __name__ == '__main__':
    logger.info("Start with configuration: \n%s", pformat(app_settings.model_dump()))
    uvicorn.run(app, host='localhost', port=10000)
