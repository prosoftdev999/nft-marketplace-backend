from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.api.dependencies import CurrentUser
from app.services.storage_service import (
    delete_image,
    upload_image,
)

router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)


class UploadResponse(BaseModel):
    object_name: str
    url: str


@router.post(
    "/images",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_nft_image(
    current_user: CurrentUser,
    file: UploadFile = File(...),
) -> UploadResponse:
    content = await file.read()

    result = upload_image(
        file=file,
        content=content,
        user_id=current_user.id,
    )

    return UploadResponse(
        **result
    )


@router.delete(
    "/images/{object_name:path}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_nft_image(
    object_name: str,
    current_user: CurrentUser,
) -> None:
    expected_prefix = (
        f"users/{current_user.id}/"
    )

    if not object_name.startswith(
        expected_prefix
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You may only delete your own uploads",
        )

    delete_image(
        object_name
    )
