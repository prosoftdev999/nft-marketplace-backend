from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.nft import NFTRead


class FavoriteRead(BaseModel):
    id: int
    user_id: int
    nft_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FavoriteWithNFT(BaseModel):
    id: int
    created_at: datetime
    nft: NFTRead

    model_config = ConfigDict(from_attributes=True)
