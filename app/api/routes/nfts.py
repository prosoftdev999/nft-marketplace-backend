from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser, DBSession
from app.models.collection import Collection
from app.models.nft import NFT
from app.schemas.nft import NFTCreate, NFTRead, NFTUpdate

router = APIRouter(
    prefix="/nfts",
    tags=["NFTs"],
)


async def get_nft_or_404(
    db: AsyncSession,
    nft_id: int,
) -> NFT:
    result = await db.execute(
        select(NFT).where(NFT.id == nft_id)
    )

    nft = result.scalar_one_or_none()

    if nft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NFT not found",
        )

    return nft


@router.post(
    "",
    response_model=NFTRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_nft(
    payload: NFTCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> NFT:
    collection_result = await db.execute(
        select(Collection).where(
            Collection.id == payload.collection_id
        )
    )

    collection = collection_result.scalar_one_or_none()

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )

    if collection.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the collection creator can add NFTs",
        )

    nft = NFT(
        **payload.model_dump(),
        owner_id=current_user.id,
        creator_id=current_user.id,
    )

    db.add(nft)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An NFT with this contract address and token ID already exists",
        ) from exc

    await db.refresh(nft)

    return nft


@router.get(
    "",
    response_model=list[NFTRead],
)
async def list_nfts(
    db: DBSession,
    collection_id: int | None = None,
    owner_id: int | None = None,
    creator_id: int | None = None,
    blockchain: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> list[NFT]:
    statement = select(NFT)

    if collection_id is not None:
        statement = statement.where(
            NFT.collection_id == collection_id
        )

    if owner_id is not None:
        statement = statement.where(
            NFT.owner_id == owner_id
        )

    if creator_id is not None:
        statement = statement.where(
            NFT.creator_id == creator_id
        )

    if blockchain is not None:
        statement = statement.where(
            NFT.blockchain == blockchain
        )

    result = await db.execute(
        statement
        .order_by(NFT.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    return list(result.scalars().all())


@router.get(
    "/{nft_id}",
    response_model=NFTRead,
)
async def get_nft(
    nft_id: int,
    db: DBSession,
) -> NFT:
    return await get_nft_or_404(
        db,
        nft_id,
    )


@router.patch(
    "/{nft_id}",
    response_model=NFTRead,
)
async def update_nft(
    nft_id: int,
    payload: NFTUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> NFT:
    nft = await get_nft_or_404(
        db,
        nft_id,
    )

    if nft.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the NFT owner can update it",
        )

    update_data = payload.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(nft, field, value)

    await db.commit()
    await db.refresh(nft)

    return nft


@router.delete(
    "/{nft_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_nft(
    nft_id: int,
    current_user: CurrentUser,
    db: DBSession,
) -> None:
    nft = await get_nft_or_404(
        db,
        nft_id,
    )

    if nft.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the NFT owner can delete it",
        )

    await db.delete(nft)
    await db.commit()
