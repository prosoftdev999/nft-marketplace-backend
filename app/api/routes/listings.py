from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser, DBSession
from app.models.listing import Listing, ListingStatus
from app.models.nft import NFT
from app.schemas.listing import ListingCreate, ListingRead

router = APIRouter(
    prefix="/listings",
    tags=["Listings"],
)


async def get_listing_or_404(
    db: AsyncSession,
    listing_id: int,
    lock: bool = False,
) -> Listing:
    statement = select(Listing).where(
        Listing.id == listing_id
    )

    if lock:
        statement = statement.with_for_update()

    result = await db.execute(statement)
    listing = result.scalar_one_or_none()

    if listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )

    return listing


@router.post(
    "",
    response_model=ListingRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_listing(
    payload: ListingCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> Listing:
    nft_result = await db.execute(
        select(NFT).where(NFT.id == payload.nft_id)
    )
    nft = nft_result.scalar_one_or_none()

    if nft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NFT not found",
        )

    if nft.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the NFT owner can list it",
        )

    active_result = await db.execute(
        select(Listing).where(
            Listing.nft_id == payload.nft_id,
            Listing.status == ListingStatus.ACTIVE,
        )
    )

    if active_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="NFT already has an active listing",
        )

    listing = Listing(
        nft_id=payload.nft_id,
        seller_id=current_user.id,
        price=payload.price,
        currency=payload.currency.upper(),
        status=ListingStatus.ACTIVE,
        listed_at=datetime.now(timezone.utc),
    )

    db.add(listing)
    await db.commit()
    await db.refresh(listing)

    return listing


@router.get(
    "",
    response_model=list[ListingRead],
)
async def list_listings(
    db: DBSession,
    listing_status: ListingStatus | None = Query(
        default=None,
        alias="status",
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> list[Listing]:
    statement = select(Listing)

    if listing_status is not None:
        statement = statement.where(
            Listing.status == listing_status
        )

    result = await db.execute(
        statement
        .order_by(Listing.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    return list(result.scalars().all())


@router.get(
    "/{listing_id}",
    response_model=ListingRead,
)
async def get_listing(
    listing_id: int,
    db: DBSession,
) -> Listing:
    return await get_listing_or_404(
        db,
        listing_id,
    )


@router.post(
    "/{listing_id}/buy",
    response_model=ListingRead,
)
async def buy_listing(
    listing_id: int,
    current_user: CurrentUser,
    db: DBSession,
) -> Listing:
    listing = await get_listing_or_404(
        db,
        listing_id,
        lock=True,
    )

    if listing.status != ListingStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Listing is not active",
        )

    if listing.seller_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seller cannot buy their own listing",
        )

    nft_result = await db.execute(
        select(NFT)
        .where(NFT.id == listing.nft_id)
        .with_for_update()
    )
    nft = nft_result.scalar_one()

    if nft.owner_id != listing.seller_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seller no longer owns this NFT",
        )

    nft.owner_id = current_user.id
    listing.buyer_id = current_user.id
    listing.status = ListingStatus.SOLD
    listing.sold_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(listing)

    return listing


@router.post(
    "/{listing_id}/cancel",
    response_model=ListingRead,
)
async def cancel_listing(
    listing_id: int,
    current_user: CurrentUser,
    db: DBSession,
) -> Listing:
    listing = await get_listing_or_404(
        db,
        listing_id,
        lock=True,
    )

    if listing.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the seller can cancel this listing",
        )

    if listing.status != ListingStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only active listings can be cancelled",
        )

    listing.status = ListingStatus.CANCELLED
    listing.cancelled_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(listing)

    return listing
