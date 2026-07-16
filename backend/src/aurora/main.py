from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from aurora.api.health import router as health_router
from aurora.core.config import settings
from aurora.core.logging import configure_logging
from aurora.api.v1.router import api_router




@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    logger.info("Aurora backend starting...")

    yield

    logger.info("Aurora backend shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(health_router)

app.include_router(api_router, prefix="/api/v1")