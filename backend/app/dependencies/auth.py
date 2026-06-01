from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession

from jose import JWTError

from app.core.config import settings
from app.core.security import verify_supabase_jwt
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import sync_authenticated_user


token_cookie = APIKeyCookie(
    name=settings.AUTH_COOKIE_NAME,
    auto_error=False,
)


async def get_current_user(
    token: str | None = Security(token_cookie),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Authenticate user using Supabase JWT token.
    Extracts user from JWT, resolves local User record,
    and synchronizes teacher role based on teachers table.
    """

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = await verify_supabase_jwt(token)
        user = await sync_authenticated_user(db, payload)
    except (JWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive account",
        )

    return user