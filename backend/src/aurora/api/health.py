from fastapi import APIRouter
from loguru import logger

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    logger.info("Health endpoint accessed")

    return {
        "status": "healthy",
        "service": "Aurora",
    }