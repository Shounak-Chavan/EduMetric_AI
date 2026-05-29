from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.enums import UserRole
from app.models.teacher import Teacher
from app.models.user import User


async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Authenticate user using Supabase JWT token.
    Extracts user from JWT, resolves local User record,
    and synchronizes teacher role based on teachers table.
    """

    try:
        scheme, token = authorization.split()

        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    try:
        # TODO:
        # Replace with proper Supabase JWT signature
        # verification using JWKS in production.
        payload = jwt.get_unverified_claims(token)

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims",
            )

        try:
            user_id_uuid = UUID(user_id)

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format in token",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    result = await db.execute(
        select(User).where(
            User.id == user_id_uuid
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive account",
        )

    # Preserve SUPER_ADMIN role
    if user.role == UserRole.SUPER_ADMIN:
        return user

    # Teachers table is source of truth
    teacher_result = await db.execute(
        select(Teacher).where(
            Teacher.user_id == user.id
        )
    )

    is_teacher = (
        teacher_result.scalar_one_or_none()
        is not None
    )

    expected_role = (
        UserRole.TEACHER
        if is_teacher
        else UserRole.STUDENT
    )

    if user.role != expected_role:
        user.role = expected_role

        await db.commit()
        await db.refresh(user)

    return user