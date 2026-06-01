from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.core.config import settings
from app.core.security import verify_supabase_jwt
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import MessageResponse, SessionTokenRequest
from app.schemas.user import UserResponse
from app.services.auth_service import sync_authenticated_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=settings.AUTH_COOKIE_MAX_AGE_SECONDS,
        path="/",
    )


def _clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.AUTH_COOKIE_NAME,
        path="/",
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


@router.post(
    "/session",
    response_model=MessageResponse,
)
async def create_session(
    data: SessionTokenRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    try:
        claims = await verify_supabase_jwt(data.token)
        await sync_authenticated_user(db, claims)
    except (JWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    _set_auth_cookie(response, data.token)
    return MessageResponse(message="Session created")


@router.post(
    "/dev-session",
    response_model=MessageResponse,
)
async def create_dev_session(
    data: SessionTokenRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    try:
        claims = await verify_supabase_jwt(data.token)
        await sync_authenticated_user(db, claims)
    except (JWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    _set_auth_cookie(response, data.token)
    return MessageResponse(message="Session created")


@router.post(
    "/logout",
    response_model=MessageResponse,
)
async def logout(response: Response):
    _clear_auth_cookie(response)
    return MessageResponse(message="Logged out")


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):
    return UserResponse.model_validate(
        current_user
    )


@router.post(
    "/sync",
    response_model=UserResponse,
)
async def sync_user(
    current_user: User = Depends(
        get_current_user
    ),
):
    return UserResponse.model_validate(
        current_user
    )