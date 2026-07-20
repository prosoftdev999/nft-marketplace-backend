from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NFT Marketplace Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str

    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    redis_url: str

    storage_provider: str = "minio"
    s3_endpoint_url: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket_name: str = "nft-assets"
    s3_region: str = "us-east-1"
    s3_public_url: str

    max_upload_size_mb: int = 10
    allowed_image_types: str = "image/jpeg,image/png,image/webp"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_image_type_set(self) -> set[str]:
        return {
            item.strip()
            for item in self.allowed_image_types.split(",")
            if item.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
