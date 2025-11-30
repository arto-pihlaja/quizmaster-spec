"""User service for profile management."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User


class UserService:
    """Service for user profile operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the user service.

        Args:
            db: Async database session.
        """
        self.db = db

    async def get_user(self, user_id: str) -> User | None:
        """Get a user by ID.

        Args:
            user_id: The user's ID.

        Returns:
            The user if found, None otherwise.
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_profile(
        self,
        user_id: str,
        display_name: str | None = None,
    ) -> User | None:
        """Update a user's profile.

        Args:
            user_id: The user's ID.
            display_name: New display name (optional).

        Returns:
            The updated user if found, None otherwise.
        """
        user = await self.get_user(user_id)
        if user is None:
            return None

        if display_name is not None:
            # Validate display name
            display_name = display_name.strip()
            if len(display_name) < 1 or len(display_name) > 50:
                return None
            user.display_name = display_name

        user.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(user)

        return user
