"""Shared API dependencies."""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..services.auth import AuthService
from ..models.user import User


# Session cookie name - must match auth.py
SESSION_COOKIE_NAME = "session_id"

# Type alias for database session
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DbSession,
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> User:
    """Get the current authenticated user from session cookie.

    This dependency can be used in any route that requires authentication.

    Args:
        db: Database session.
        session_id: Session cookie value.

    Returns:
        The authenticated user.

    Raises:
        HTTPException: If not authenticated.
    """
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    service = AuthService(db)
    user = await service.get_user_by_session_token(session_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    return user


async def get_optional_user(
    db: DbSession,
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> User | None:
    """Get the current user if authenticated, None otherwise.

    This dependency can be used in routes that optionally use auth.

    Args:
        db: Database session.
        session_id: Session cookie value.

    Returns:
        The authenticated user or None.
    """
    if not session_id:
        return None

    service = AuthService(db)
    return await service.get_user_by_session_token(session_id)


async def require_admin(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require the current user to be an admin.

    This dependency extends get_current_user to also check admin status.

    Args:
        user: The authenticated user.

    Returns:
        The authenticated admin user.

    Raises:
        HTTPException: If user is not an admin.
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user


# Type aliases for use in route handlers
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
AdminUser = Annotated[User, Depends(require_admin)]
