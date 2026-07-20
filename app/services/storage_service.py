from functools import lru_cache
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


@lru_cache
def get_s3_client() -> BaseClient:
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    )


def ensure_bucket_exists() -> None:
    client = get_s3_client()

    try:
        client.head_bucket(
            Bucket=settings.s3_bucket_name
        )
    except ClientError:
        client.create_bucket(
            Bucket=settings.s3_bucket_name
        )


def validate_image(
    file: UploadFile,
    content: bytes,
) -> None:
    if file.content_type not in settings.allowed_image_type_set:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                "Unsupported image type. "
                f"Allowed types: {sorted(settings.allowed_image_type_set)}"
            ),
        )

    maximum_size = (
        settings.max_upload_size_mb
        * 1024
        * 1024
    )

    if len(content) > maximum_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Maximum upload size is "
                f"{settings.max_upload_size_mb} MB"
            ),
        )


def upload_image(
    file: UploadFile,
    content: bytes,
    user_id: int,
) -> dict[str, str]:
    validate_image(
        file,
        content,
    )

    extension = Path(
        file.filename or "image"
    ).suffix.lower()

    object_name = (
        f"users/{user_id}/"
        f"{uuid4().hex}{extension}"
    )

    client = get_s3_client()

    client.put_object(
        Bucket=settings.s3_bucket_name,
        Key=object_name,
        Body=content,
        ContentType=(
            file.content_type
            or "application/octet-stream"
        ),
    )

    public_url = (
        f"{settings.s3_public_url.rstrip('/')}/"
        f"{object_name}"
    )

    return {
        "object_name": object_name,
        "url": public_url,
    }


def delete_image(
    object_name: str,
) -> None:
    get_s3_client().delete_object(
        Bucket=settings.s3_bucket_name,
        Key=object_name,
    )
