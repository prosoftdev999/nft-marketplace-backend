from fastapi import APIRouter

from app.api.routes import (
    auth,
    collections,
    favorites,
    listings,
    nfts,
    search,
    uploads,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(collections.router)
api_router.include_router(nfts.router)
api_router.include_router(uploads.router)
api_router.include_router(listings.router)
api_router.include_router(favorites.router)
api_router.include_router(search.router)
