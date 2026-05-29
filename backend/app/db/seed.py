from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.supabase import supabase
from app.models.enums import UserRole
from app.models.user import User


async def seed_admin(db: AsyncSession) -> None:
    result = await db.execute(
        select(User).where(
            User.email == settings.SUPER_ADMIN_EMAIL
        )
    )

    existing_admin = result.scalar_one_or_none()

    if existing_admin:
        print("Super Admin Already Exists")
        return

    auth_user = supabase.auth.admin.create_user(
        {
            "email": settings.SUPER_ADMIN_EMAIL,
            "password": settings.SUPER_ADMIN_PASSWORD,
            "email_confirm": True,
        }
    )

    user = auth_user.user

    admin = User(
        id=UUID(user.id),
        email=user.email,
        full_name=settings.SUPER_ADMIN_NAME,
        role=UserRole.SUPER_ADMIN,
        is_active=True,
    )

    db.add(admin)

    await db.commit()

    print("Super Admin Created")