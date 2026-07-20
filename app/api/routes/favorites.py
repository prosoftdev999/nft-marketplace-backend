from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.dependencies import CurrentUser, DBSession
from app.models.favorite import Favorite
from app.models.nft import NFT
from app.schemas.favorite import FavoriteRead, FavoriteWithNFT

router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"],
)


@router.post(
    "/{nft_id}",
    response_model=FavoriteRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_favorite(
    nft_id: int,
    current_user: CurrentUser,
    db: DBSession,
) -> Favorite:
    nft_result = await db.execute(
        select(NFT).where(NFT.id == nft_id)
    )

    nft = nft_result.scalar_one_or_none()

    if nft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NFT not found",
        )

    favorite_result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.nft_id == nft_id,
        )
    )

    if favorite_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="NFT is already in favorites",
        )

    favorite = Favorite(
        user_id=current_user.id,
        nft_id=nft_id,
    )

    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)

    return favorite


@router.get(
    "/me",
    response_model=list[FavoriteWithNFT],
)
async def list_my_favorites(
    current_user: CurrentUser,
    db: DBSession,
) -> list[Favorite]:
    result = await db.execute(
        select(Favorite)
        .options(
            selectinload(Favorite.nft)
        )
        .where(
            Favorite.user_id == current_user.id
        )
        .order_by(
            Favorite.created_at.desc()
        )
    )

    return list(
        result.scalars().unique().all()
    )


@router.delete(
    "/{nft_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_favorite(
    nft_id: int,
    current_user: CurrentUser,
    db: DBSession,
) -> None:
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.nft_id == nft_id,
        )
    )

    favorite = result.scalar_one_or_none()

    if favorite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )

    await db.delete(favorite)
    await db.commit()
