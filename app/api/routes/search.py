from fastapi import APIRouter, Query
from sqlalchemy import or_, select

from app.api.dependencies import DBSession
from app.models.collection import Collection
from app.models.nft import NFT
from app.schemas.collection import CollectionRead
from app.schemas.nft import NFTRead

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get(
    "/nfts",
    response_model=list[NFTRead],
)
async def search_nfts(
    db: DBSession,
    q: str = Query(min_length=1, max_length=100),
    blockchain: str | None = None,
    collection_id: int | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> list[NFT]:
    pattern = f"%{q}%"

    statement = select(NFT).where(
        or_(
            NFT.name.ilike(pattern),
            NFT.description.ilike(pattern),
            NFT.token_id.ilike(pattern),
        )
    )

    if blockchain is not None:
        statement = statement.where(
            NFT.blockchain == blockchain
        )

    if collection_id is not None:
        statement = statement.where(
            NFT.collection_id == collection_id
        )

    result = await db.execute(
        statement
        .order_by(NFT.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    return list(result.scalars().all())


@router.get(
    "/collections",
    response_model=list[CollectionRead],
)
async def search_collections(
    db: DBSession,
    q: str = Query(min_length=1, max_length=100),
    blockchain: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> list[Collection]:
    pattern = f"%{q}%"

    statement = select(Collection).where(
        or_(
            Collection.name.ilike(pattern),
            Collection.slug.ilike(pattern),
            Collection.description.ilike(pattern),
        )
    )

    if blockchain is not None:
        statement = statement.where(
            Collection.blockchain == blockchain
        )

    result = await db.execute(
        statement
        .order_by(Collection.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    return list(result.scalars().all())
