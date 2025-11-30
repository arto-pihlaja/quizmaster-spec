"""Authentication service for user registration, login, logout, and password reset."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from ..models.session import Session
from ..models.login_attempt import LoginAttempt
from ..models.password_reset import PasswordReset
from ..security.password import hash_password, verify_password, validate_password_strength
from ..security.tokens import generate_session_token, generate_reset_token, hash_token


# Lockout configuration: attempts -> wait time in minutes
LOCKOUT_SCHEDULE = {
    6: 1,    # 6th attempt: 1 minute
    7: 5,    # 7th attempt: 5 minutes
    8: 15,   # 8th attempt: 15 minutes
    9: 30,   # 9th+ attempt: 30 minutes
}


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the auth service.

        Args:
            db: Async database session.
        """
        self.db = db

    # ==================== Registration ====================

    async def register_user(
        self,
        email: str,
        password: str,
        display_name: str,
    ) -> tuple[User | None, str | None]:
        """Register a new user.

        Args:
            email: User's email address.
            password: User's password (plain text).
            display_name: User's display name.

        Returns:
            Tuple of (user, error_message).
            If successful, user is returned and error is None.
            If failed, user is None and error contains the reason.
        """
        # Normalize email to lowercase
        email = email.lower().strip()

        # Validate password strength
        is_valid, error = validate_password_strength(password)
        if not is_valid:
            return None, error

        # Check if email already exists
        existing = await self._get_user_by_email(email)
        if existing:
            return None, "Email already registered"

        # Check if this is the first user (will be admin)
        is_first_user = await self._is_first_user()

        # Create user
        user = User(
            id=str(uuid4()),
            email=email,
            password_hash=hash_password(password),
            display_name=display_name.strip(),
            is_admin=is_first_user,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user, None

    async def _get_user_by_email(self, email: str) -> User | None:
        """Get a user by email address."""
        result = await self.db.execute(
            select(User).where(func.lower(User.email) == email.lower())
        )
        return result.scalar_one_or_none()

    async def _is_first_user(self) -> bool:
        """Check if this will be the first user in the system."""
        result = await self.db.execute(select(func.count(User.id)))
        count = result.scalar()
        return count == 0

    # ==================== Login ====================

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate a user by email and password.

        Args:
            email: User's email address.
            password: User's password (plain text).

        Returns:
            The user if authentication successful, None otherwise.
        """
        user = await self._get_user_by_email(email)
        if user is None:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    async def create_session(
        self,
        user: User,
        user_agent: str | None = None,
        ip_address: str | None = None,
        days_valid: int = 7,
    ) -> Session:
        """Create a new session for a user.

        Args:
            user: The user to create a session for.
            user_agent: The user agent string from the request.
            ip_address: The client IP address.
            days_valid: Number of days the session is valid.

        Returns:
            The created session.
        """
        session = Session(
            id=str(uuid4()),
            user_id=user.id,
            token=generate_session_token(),
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=days_valid),
            user_agent=user_agent,
            ip_address=ip_address,
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def get_session_by_token(self, token: str) -> Session | None:
        """Get a valid session by token.

        Args:
            token: The session token.

        Returns:
            The session if valid and not expired, None otherwise.
        """
        result = await self.db.execute(
            select(Session).where(
                Session.token == token,
                Session.expires_at > datetime.utcnow(),
            )
        )
        return result.scalar_one_or_none()

    async def get_user_by_session_token(self, token: str) -> User | None:
        """Get a user by their session token.

        Args:
            token: The session token.

        Returns:
            The user if session is valid, None otherwise.
        """
        session = await self.get_session_by_token(token)
        if session is None:
            return None

        result = await self.db.execute(
            select(User).where(User.id == session.user_id)
        )
        return result.scalar_one_or_none()

    # ==================== Logout ====================

    async def invalidate_session(self, token: str) -> bool:
        """Invalidate a session by deleting it.

        Args:
            token: The session token to invalidate.

        Returns:
            True if session was found and deleted, False otherwise.
        """
        result = await self.db.execute(
            select(Session).where(Session.token == token)
        )
        session = result.scalar_one_or_none()

        if session is None:
            return False

        await self.db.delete(session)
        await self.db.commit()
        return True

    async def invalidate_all_user_sessions(self, user_id: str) -> int:
        """Invalidate all sessions for a user.

        Args:
            user_id: The user's ID.

        Returns:
            Number of sessions invalidated.
        """
        result = await self.db.execute(
            select(Session).where(Session.user_id == user_id)
        )
        sessions = result.scalars().all()

        for session in sessions:
            await self.db.delete(session)

        await self.db.commit()
        return len(sessions)

    # ==================== Password Reset ====================

    async def request_password_reset(self, email: str) -> str | None:
        """Request a password reset for an email.

        Args:
            email: The email address.

        Returns:
            The reset token if user exists, None otherwise.
            Note: Caller should not reveal whether email exists.
        """
        user = await self._get_user_by_email(email)
        if user is None:
            return None

        # Invalidate any existing reset tokens for this user
        await self._invalidate_user_reset_tokens(user.id)

        # Generate new token
        token = generate_reset_token()
        token_hash = hash_token(token)

        # Create reset record
        reset = PasswordReset(
            id=str(uuid4()),
            user_id=user.id,
            token_hash=token_hash,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            used=False,
        )

        self.db.add(reset)
        await self.db.commit()

        return token

    async def _invalidate_user_reset_tokens(self, user_id: str) -> None:
        """Invalidate all pending reset tokens for a user."""
        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.user_id == user_id,
                PasswordReset.used == False,  # noqa: E712
            )
        )
        tokens = result.scalars().all()

        for token in tokens:
            token.used = True
            token.used_at = datetime.utcnow()

        await self.db.commit()

    async def reset_password(self, token: str, new_password: str) -> tuple[bool, str | None]:
        """Reset a user's password using a reset token.

        Args:
            token: The reset token from the email.
            new_password: The new password.

        Returns:
            Tuple of (success, error_message).
        """
        # Validate password strength
        is_valid, error = validate_password_strength(new_password)
        if not is_valid:
            return False, error

        # Find and validate the token
        token_hash = hash_token(token)
        result = await self.db.execute(
            select(PasswordReset).where(PasswordReset.token_hash == token_hash)
        )
        reset = result.scalar_one_or_none()

        if reset is None:
            return False, "Invalid or expired reset token"

        if not reset.is_valid:
            return False, "Reset token has already been used or expired"

        # Get the user
        result = await self.db.execute(
            select(User).where(User.id == reset.user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return False, "User not found"

        # Update password
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()

        # Mark token as used
        reset.used = True
        reset.used_at = datetime.utcnow()

        # Invalidate all user sessions (security measure)
        await self.invalidate_all_user_sessions(user.id)

        await self.db.commit()
        return True, None

    # ==================== Account Lockout ====================

    async def check_lockout(self, email: str) -> tuple[bool, datetime | None]:
        """Check if an account is locked out.

        Args:
            email: The email address to check.

        Returns:
            Tuple of (is_locked, locked_until).
        """
        result = await self.db.execute(
            select(LoginAttempt).where(
                func.lower(LoginAttempt.email) == email.lower()
            )
        )
        attempt = result.scalar_one_or_none()

        if attempt is None:
            return False, None

        if attempt.is_locked:
            return True, attempt.locked_until

        return False, None

    async def record_failed_attempt(self, email: str) -> tuple[int, datetime | None]:
        """Record a failed login attempt.

        Args:
            email: The email address that failed to login.

        Returns:
            Tuple of (attempt_count, locked_until).
        """
        email = email.lower()

        result = await self.db.execute(
            select(LoginAttempt).where(
                func.lower(LoginAttempt.email) == email
            )
        )
        attempt = result.scalar_one_or_none()

        if attempt is None:
            attempt = LoginAttempt(
                id=str(uuid4()),
                email=email,
                attempt_count=1,
                last_attempt_at=datetime.utcnow(),
            )
            self.db.add(attempt)
        else:
            attempt.attempt_count += 1
            attempt.last_attempt_at = datetime.utcnow()

        # Calculate lockout if needed
        locked_until = None
        if attempt.attempt_count >= 6:
            lockout_minutes = LOCKOUT_SCHEDULE.get(
                attempt.attempt_count,
                LOCKOUT_SCHEDULE[9],  # Default to max lockout
            )
            locked_until = datetime.utcnow() + timedelta(minutes=lockout_minutes)
            attempt.locked_until = locked_until

        await self.db.commit()
        return attempt.attempt_count, locked_until

    async def clear_lockout(self, email: str) -> None:
        """Clear lockout status for an email after successful login.

        Args:
            email: The email address.
        """
        result = await self.db.execute(
            select(LoginAttempt).where(
                func.lower(LoginAttempt.email) == email.lower()
            )
        )
        attempt = result.scalar_one_or_none()

        if attempt:
            await self.db.delete(attempt)
            await self.db.commit()
