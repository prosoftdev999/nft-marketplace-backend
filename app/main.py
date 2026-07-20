import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.services.storage_service import ensure_bucket_exists

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        ensure_bucket_exists()
    except Exception:
        logger.warning(
            "MinIO/S3 is not available yet. "
            "Image uploads will work after storage starts.",
            exc_info=True,
        )

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Backend API for NFT metadata, collections, marketplace listings, "
        "favorites, authentication, search, and MinIO/S3 image uploads."
    ),
    lifespan=lifespan,
)

app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)


@app.get(
    "/",
    tags=["System"],
)
async def root() -> dict[str, str]:
    return {
        "message": "NFT Marketplace Backend is running",
    }


@app.get(
    "/health",
    tags=["System"],
)
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
    }
