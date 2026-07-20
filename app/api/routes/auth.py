from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import CurrentUser, DBSession
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserRead

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: UserCreate,
    db: DBSession,
) -> User:
    result = await db.execute(
        select(User).where(
            or_(
                User.email == payload.email,
                User.username == payload.username,
            )
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already exists",
        )

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        wallet_address=payload.wallet_address,
    )

    db.add(user)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email, username, or wallet address already exists",
        ) from exc

    await db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    form: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    db: DBSession,
) -> TokenResponse:
    result = await db.execute(
        select(User).where(
            or_(
                User.email == form.username,
                User.username == form.username,
            )
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(
        form.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token = create_access_token(
        subject=str(user.id),
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserRead.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserRead,
)
async def get_me(
    current_user: CurrentUser,
) -> User:
    return current_user
