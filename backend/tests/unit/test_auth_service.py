"""Unit tests for AuthService."""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.auth import AuthService
from src.models.user import User
from src.models.session import Session


class TestRegisterUser:
    """Tests for AuthService.register_user."""

    @pytest.mark.asyncio
    async def test_register_user_creates_user(self, db_session):
        """register_user creates a new user."""
        service = AuthService(db_session)
        user, error = await service.register_user(
            email="test@example.com",
            password="SecurePass123",
            display_name="TestUser",
        )

        assert user is not None
        assert error is None
        assert user.email == "test@example.com"
        assert user.display_name == "TestUser"

    @pytest.mark.asyncio
    async def test_register_user_normalizes_email(self, db_session):
        """register_user normalizes email to lowercase."""
        service = AuthService(db_session)
        user, error = await service.register_user(
            email="TEST@EXAMPLE.COM",
            password="SecurePass123",
            display_name="TestUser",
        )

        assert user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_register_user_hashes_password(self, db_session):
        """register_user stores hashed password."""
        service = AuthService(db_session)
        user, error = await service.register_user(
            email="test@example.com",
            password="SecurePass123",
            display_name="TestUser",
        )

        assert user.password_hash != "SecurePass123"
        assert user.password_hash.startswith("$2b$")

    @pytest.mark.asyncio
    async def test_register_user_first_user_is_admin(self, db_session):
        """First registered user becomes admin."""
        service = AuthService(db_session)
        user, error = await service.register_user(
            email="admin@example.com",
            password="SecurePass123",
            display_name="Admin",
        )

        assert user.is_admin is True

    @pytest.mark.asyncio
    async def test_register_user_subsequent_not_admin(self, db_session):
        """Subsequent users are not admin."""
        service = AuthService(db_session)

        # First user
        await service.register_user(
            email="admin@example.com",
            password="SecurePass123",
            display_name="Admin",
        )

        # Second user
        user, error = await service.register_user(
            email="user@example.com",
            password="SecurePass123",
            display_name="User",
        )

        assert user.is_admin is False

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email_fails(self, db_session):
        """register_user fails for duplicate email."""
        service = AuthService(db_session)

        await service.register_user(
            email="dupe@example.com",
            password="SecurePass123",
            display_name="First",
        )

        user, error = await service.register_user(
            email="dupe@example.com",
            password="SecurePass123",
            display_name="Second",
        )

        assert user is None
        assert "already registered" in error.lower()

    @pytest.mark.asyncio
    async def test_register_user_weak_password_fails(self, db_session):
        """register_user fails for weak password."""
        service = AuthService(db_session)

        user, error = await service.register_user(
            email="test@example.com",
            password="weak",
            display_name="Test",
        )

        assert user is None
        assert error is not None


class TestAuthenticateUser:
    """Tests for AuthService.authenticate_user."""

    @pytest_asyncio.fixture
    async def registered_user(self, db_session):
        """Create a registered user for tests."""
        service = AuthService(db_session)
        user, _ = await service.register_user(
            email="auth@example.com",
            password="SecurePass123",
            display_name="AuthUser",
        )
        return user

    @pytest.mark.asyncio
    async def test_authenticate_user_correct_password(self, db_session, registered_user):
        """authenticate_user returns user for correct password."""
        service = AuthService(db_session)
        user = await service.authenticate_user("auth@example.com", "SecurePass123")

        assert user is not None
        assert user.id == registered_user.id

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db_session, registered_user):
        """authenticate_user returns None for wrong password."""
        service = AuthService(db_session)
        user = await service.authenticate_user("auth@example.com", "WrongPassword")

        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_nonexistent_email(self, db_session):
        """authenticate_user returns None for non-existent email."""
        service = AuthService(db_session)
        user = await service.authenticate_user("nonexistent@example.com", "AnyPassword")

        assert user is None


class TestCreateSession:
    """Tests for AuthService.create_session."""

    @pytest_asyncio.fixture
    async def registered_user(self, db_session):
        """Create a registered user for tests."""
        service = AuthService(db_session)
        user, _ = await service.register_user(
            email="session@example.com",
            password="SecurePass123",
            display_name="SessionUser",
        )
        return user

    @pytest.mark.asyncio
    async def test_create_session_returns_session(self, db_session, registered_user):
        """create_session returns a session object."""
        service = AuthService(db_session)
        session = await service.create_session(registered_user)

        assert session is not None
        assert session.user_id == registered_user.id
        assert session.token is not None

    @pytest.mark.asyncio
    async def test_create_session_sets_expiry(self, db_session, registered_user):
        """create_session sets correct expiry."""
        service = AuthService(db_session)
        session = await service.create_session(registered_user, days_valid=7)

        assert session.expires_at > datetime.utcnow()
        assert session.expires_at < datetime.utcnow() + timedelta(days=8)

    @pytest.mark.asyncio
    async def test_create_session_stores_user_agent(self, db_session, registered_user):
        """create_session stores user agent."""
        service = AuthService(db_session)
        session = await service.create_session(
            registered_user,
            user_agent="Mozilla/5.0",
        )

        assert session.user_agent == "Mozilla/5.0"


class TestInvalidateSession:
    """Tests for AuthService.invalidate_session."""

    @pytest_asyncio.fixture
    async def user_with_session(self, db_session):
        """Create a user with an active session."""
        service = AuthService(db_session)
        user, _ = await service.register_user(
            email="invalidate@example.com",
            password="SecurePass123",
            display_name="InvalidateUser",
        )
        session = await service.create_session(user)
        return user, session

    @pytest.mark.asyncio
    async def test_invalidate_session_deletes_session(self, db_session, user_with_session):
        """invalidate_session deletes the session."""
        user, session = user_with_session
        service = AuthService(db_session)

        result = await service.invalidate_session(session.token)

        assert result is True

        # Verify session is gone
        found = await service.get_session_by_token(session.token)
        assert found is None

    @pytest.mark.asyncio
    async def test_invalidate_session_nonexistent_returns_false(self, db_session):
        """invalidate_session returns False for non-existent session."""
        service = AuthService(db_session)
        result = await service.invalidate_session("nonexistent_token")

        assert result is False


class TestPasswordReset:
    """Tests for password reset functionality."""

    @pytest_asyncio.fixture
    async def registered_user(self, db_session):
        """Create a registered user for tests."""
        service = AuthService(db_session)
        user, _ = await service.register_user(
            email="reset@example.com",
            password="SecurePass123",
            display_name="ResetUser",
        )
        return user

    @pytest.mark.asyncio
    async def test_request_password_reset_returns_token(self, db_session, registered_user):
        """request_password_reset returns a token for existing user."""
        service = AuthService(db_session)
        token = await service.request_password_reset("reset@example.com")

        assert token is not None
        assert len(token) > 20

    @pytest.mark.asyncio
    async def test_request_password_reset_nonexistent_returns_none(self, db_session):
        """request_password_reset returns None for non-existent email."""
        service = AuthService(db_session)
        token = await service.request_password_reset("nonexistent@example.com")

        assert token is None

    @pytest.mark.asyncio
    async def test_reset_password_with_valid_token(self, db_session, registered_user):
        """reset_password works with valid token."""
        service = AuthService(db_session)
        token = await service.request_password_reset("reset@example.com")

        success, error = await service.reset_password(token, "NewSecurePass123")

        assert success is True
        assert error is None

        # Verify new password works
        user = await service.authenticate_user("reset@example.com", "NewSecurePass123")
        assert user is not None

    @pytest.mark.asyncio
    async def test_reset_password_with_invalid_token(self, db_session):
        """reset_password fails with invalid token."""
        service = AuthService(db_session)

        success, error = await service.reset_password("invalid_token", "NewSecurePass123")

        assert success is False
        assert "invalid" in error.lower() or "expired" in error.lower()

    @pytest.mark.asyncio
    async def test_reset_password_invalidates_token(self, db_session, registered_user):
        """reset_password invalidates the token after use."""
        service = AuthService(db_session)
        token = await service.request_password_reset("reset@example.com")

        # First reset succeeds
        success1, _ = await service.reset_password(token, "NewSecurePass123")
        assert success1 is True

        # Second reset fails
        success2, error2 = await service.reset_password(token, "AnotherPass123")
        assert success2 is False


class TestAccountLockout:
    """Tests for account lockout functionality."""

    @pytest.mark.asyncio
    async def test_check_lockout_not_locked(self, db_session):
        """check_lockout returns False for non-locked account."""
        service = AuthService(db_session)
        is_locked, _ = await service.check_lockout("test@example.com")

        assert is_locked is False

    @pytest.mark.asyncio
    async def test_record_failed_attempt_increments_count(self, db_session):
        """record_failed_attempt increments attempt count."""
        service = AuthService(db_session)

        count1, _ = await service.record_failed_attempt("test@example.com")
        count2, _ = await service.record_failed_attempt("test@example.com")

        assert count2 > count1

    @pytest.mark.asyncio
    async def test_lockout_after_6_attempts(self, db_session):
        """Account is locked after 6 failed attempts."""
        service = AuthService(db_session)

        # Make 6 failed attempts
        for _ in range(6):
            await service.record_failed_attempt("lockout@example.com")

        is_locked, locked_until = await service.check_lockout("lockout@example.com")

        assert is_locked is True
        assert locked_until is not None

    @pytest.mark.asyncio
    async def test_clear_lockout_on_success(self, db_session):
        """clear_lockout removes lockout."""
        service = AuthService(db_session)

        # Create lockout
        for _ in range(6):
            await service.record_failed_attempt("clear@example.com")

        # Clear it
        await service.clear_lockout("clear@example.com")

        is_locked, _ = await service.check_lockout("clear@example.com")
        assert is_locked is False
