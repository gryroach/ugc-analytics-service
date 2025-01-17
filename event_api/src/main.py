import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import api_router as api_v1_router
from core.config import settings
from db import redis
from middlewares.request_id import request_id_require
from services.background_tasks import process_redis_queue


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis.from_url(settings.redis_url)
    asyncio.create_task(process_redis_queue(redis.redis))
    try:
        yield
    finally:
        await redis.redis.aclose()


app = FastAPI(
    title=settings.project_name,
    description="API сервиса получения событий",
    version="1.0.0",
    docs_url="/api-event/openapi",
    openapi_url="/api-event/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.middleware("http")(request_id_require)

app.include_router(api_v1_router, prefix="/api-event/v1")
