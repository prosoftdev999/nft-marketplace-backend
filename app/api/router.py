from fastapi import APIRouter

from app.api.routes import (
    auth,
    collections,
    listings,
    nfts,
    uploads,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(collections.router)
api_router.include_router(nfts.router)
api_router.include_router(uploads.router)
api_router.include_router(listings.router)
