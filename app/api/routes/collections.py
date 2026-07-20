from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser, DBSession
from app.models.collection import Collection
from app.schemas.collection import (
    CollectionCreate,
    CollectionRead,
    CollectionUpdate,
)

router = APIRouter(
    prefix="/collections",
    tags=["Collections"],
)


async def get_collection_or_404(
    db: AsyncSession,
    collection_id: int,
) -> Collection:
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id
        )
    )

    collection = result.scalar_one_or_none()

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )

    return collection


@router.post(
    "",
    response_model=CollectionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_collection(
    payload: CollectionCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> Collection:
    result = await db.execute(
        select(Collection).where(
            Collection.slug == payload.slug
        )
    )

    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Collection slug already exists",
        )

    collection = Collection(
        **payload.model_dump(),
        creator_id=current_user.id,
    )

    db.add(collection)
    await db.commit()
    await db.refresh(collection)

    return collection


@router.get(
    "",
    response_model=list[CollectionRead],
)
async def list_collections(
    db: DBSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> list[Collection]:
    result = await db.execute(
        select(Collection)
        .order_by(Collection.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    return list(result.scalars().all())


@router.get(
    "/{collection_id}",
    response_model=CollectionRead,
)
async def get_collection(
    collection_id: int,
    db: DBSession,
) -> Collection:
    return await get_collection_or_404(
        db,
        collection_id,
    )


@router.patch(
    "/{collection_id}",
    response_model=CollectionRead,
)
async def update_collection(
    collection_id: int,
    payload: CollectionUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> Collection:
    collection = await get_collection_or_404(
        db,
        collection_id,
    )

    if collection.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the collection creator can update it",
        )

    update_data = payload.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(collection, field, value)

    await db.commit()
    await db.refresh(collection)

    return collection


@router.delete(
    "/{collection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_collection(
    collection_id: int,
    current_user: CurrentUser,
    db: DBSession,
) -> None:
    collection = await get_collection_or_404(
        db,
        collection_id,
    )

    if collection.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the collection creator can delete it",
        )

    await db.delete(collection)
    await db.commit()
