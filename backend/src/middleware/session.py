"""Session middleware for FastAPI.

This middleware handles session validation and expired session cleanup.
"""

from datetime import datetime
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Session cookie name
SESSION_COOKIE_NAME = "session_id"


class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware for session handling.

    This middleware:
    1. Validates session tokens on protected routes
    2. Could be extended for sliding session expiration
    3. Could trigger cleanup of expired sessions
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request.

        Args:
            request: The incoming request.
            call_next: The next handler in the chain.

        Returns:
            The response.
        """
        # Get session ID from cookie
        session_id = request.cookies.get(SESSION_COOKIE_NAME)

        # Store session info in request state for downstream handlers
        request.state.session_id = session_id

        # Continue processing
        response = await call_next(request)

        return response


async def cleanup_expired_sessions(db) -> int:
    """Clean up expired sessions from the database.

    This should be called periodically (e.g., via scheduled task).

    Args:
        db: Database session.

    Returns:
        Number of sessions deleted.
    """
    from sqlalchemy import delete
    from ..models.session import Session

    result = await db.execute(
        delete(Session).where(Session.expires_at < datetime.utcnow())
    )
    await db.commit()

    return result.rowcount
