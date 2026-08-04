from fastapi import FastAPI

from aurora.api.health import router as health_router
from aurora.api.v1.router import api_router

app = FastAPI(
    title="Aurora API",
    version="1.0.0",
)

app.include_router(health_router)
app.include_router(api_router, prefix="/api/v1")