"""Contract tests for Authentication API endpoints."""

import pytest
import pytest_asyncio
from httpx import AsyncClient


class TestRegisterContract:
    """Contract tests for POST /auth/register."""

    @pytest.mark.asyncio
    async def test_register_returns_201(self, client: AsyncClient):
        """Registration with valid data returns 201."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123",
                "display_name": "TestUser",
            },
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_register_response_structure(self, client: AsyncClient):
        """Registration response has correct structure."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "structure@example.com",
                "password": "SecurePass123",
                "display_name": "StructureTest",
            },
        )
        data = response.json()

        assert "message" in data
        assert "user" in data
        assert "id" in data["user"]
        assert "email" in data["user"]
        assert "display_name" in data["user"]
        assert "is_admin" in data["user"]
        assert "created_at" in data["user"]

    @pytest.mark.asyncio
    async def test_register_sets_session_cookie(self, client: AsyncClient):
        """Registration sets session cookie."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "cookie@example.com",
                "password": "SecurePass123",
                "display_name": "CookieTest",
            },
        )
        assert "session_id" in response.cookies

    @pytest.mark.asyncio
    async def test_register_duplicate_email_returns_409(self, client: AsyncClient):
        """Registration with existing email returns 409."""
        # First registration
        await client.post(
            "/auth/register",
            json={
                "email": "dupe@example.com",
                "password": "SecurePass123",
                "display_name": "FirstUser",
            },
        )

        # Duplicate registration
        response = await client.post(
            "/auth/register",
            json={
                "email": "dupe@example.com",
                "password": "SecurePass123",
                "display_name": "SecondUser",
            },
        )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_register_weak_password_returns_error(self, client: AsyncClient):
        """Registration with weak password returns 400 or 422."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "weak@example.com",
                "password": "short",  # Too short
                "display_name": "WeakPass",
            },
        )
        # FastAPI returns 422 for Pydantic validation errors
        assert response.status_code in (400, 422)


class TestLoginContract:
    """Contract tests for POST /auth/login."""

    @pytest_asyncio.fixture
    async def registered_user(self, client: AsyncClient):
        """Create a registered user for login tests."""
        await client.post(
            "/auth/register",
            json={
                "email": "login@example.com",
                "password": "SecurePass123",
                "display_name": "LoginUser",
            },
        )
        return {"email": "login@example.com", "password": "SecurePass123"}

    @pytest.mark.asyncio
    async def test_login_returns_200(self, client: AsyncClient, registered_user):
        """Login with valid credentials returns 200."""
        response = await client.post(
            "/auth/login",
            json={
                "email": registered_user["email"],
                "password": registered_user["password"],
            },
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_login_response_structure(self, client: AsyncClient, registered_user):
        """Login response has correct structure."""
        response = await client.post(
            "/auth/login",
            json={
                "email": registered_user["email"],
                "password": registered_user["password"],
            },
        )
        data = response.json()

        assert "message" in data
        assert "user" in data
        assert "id" in data["user"]
        assert "email" in data["user"]

    @pytest.mark.asyncio
    async def test_login_sets_session_cookie(self, client: AsyncClient, registered_user):
        """Login sets session cookie."""
        response = await client.post(
            "/auth/login",
            json={
                "email": registered_user["email"],
                "password": registered_user["password"],
            },
        )
        assert "session_id" in response.cookies

    @pytest.mark.asyncio
    async def test_login_invalid_credentials_returns_401(self, client: AsyncClient, registered_user):
        """Login with wrong password returns 401."""
        response = await client.post(
            "/auth/login",
            json={
                "email": registered_user["email"],
                "password": "WrongPassword123",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user_returns_401(self, client: AsyncClient):
        """Login with non-existent email returns 401 (same as wrong password)."""
        response = await client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "AnyPassword123",
            },
        )
        assert response.status_code == 401


class TestLogoutContract:
    """Contract tests for POST /auth/logout."""

    @pytest_asyncio.fixture
    async def logged_in_client(self, client: AsyncClient):
        """Create a logged-in client."""
        await client.post(
            "/auth/register",
            json={
                "email": "logout@example.com",
                "password": "SecurePass123",
                "display_name": "LogoutUser",
            },
        )
        return client

    @pytest.mark.asyncio
    async def test_logout_returns_200(self, logged_in_client: AsyncClient):
        """Logout returns 200."""
        response = await logged_in_client.post("/auth/logout")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_logout_clears_session_cookie(self, logged_in_client: AsyncClient):
        """Logout clears session cookie."""
        response = await logged_in_client.post("/auth/logout")
        # Cookie should be cleared (empty or expired)
        assert response.cookies.get("session_id", "") == "" or "session_id" not in response.cookies


class TestForgotPasswordContract:
    """Contract tests for POST /auth/forgot-password."""

    @pytest.mark.asyncio
    async def test_forgot_password_returns_200(self, client: AsyncClient):
        """Forgot password always returns 200."""
        response = await client.post(
            "/auth/forgot-password",
            json={"email": "any@example.com"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_forgot_password_same_response_for_existing_and_nonexistent(self, client: AsyncClient):
        """Forgot password returns same message for existing and non-existing emails."""
        # Create a user
        await client.post(
            "/auth/register",
            json={
                "email": "exists@example.com",
                "password": "SecurePass123",
                "display_name": "ExistingUser",
            },
        )

        # Request for existing email
        response1 = await client.post(
            "/auth/forgot-password",
            json={"email": "exists@example.com"},
        )

        # Request for non-existing email
        response2 = await client.post(
            "/auth/forgot-password",
            json={"email": "notexists@example.com"},
        )

        # Both should return same status and similar message
        assert response1.status_code == response2.status_code == 200


class TestResetPasswordContract:
    """Contract tests for POST /auth/reset-password."""

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token_returns_400(self, client: AsyncClient):
        """Reset password with invalid token returns 400."""
        response = await client.post(
            "/auth/reset-password",
            json={
                "token": "invalid_token",
                "new_password": "NewSecurePass123",
            },
        )
        assert response.status_code == 400


class TestGetMeContract:
    """Contract tests for GET /auth/me."""

    @pytest_asyncio.fixture
    async def logged_in_client(self, client: AsyncClient):
        """Create a logged-in client."""
        await client.post(
            "/auth/register",
            json={
                "email": "me@example.com",
                "password": "SecurePass123",
                "display_name": "MeUser",
            },
        )
        return client

    @pytest.mark.asyncio
    async def test_get_me_returns_200(self, logged_in_client: AsyncClient):
        """Get current user returns 200 when authenticated."""
        response = await logged_in_client.get("/auth/me")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_me_response_structure(self, logged_in_client: AsyncClient):
        """Get current user response has correct structure."""
        response = await logged_in_client.get("/auth/me")
        data = response.json()

        assert "id" in data
        assert "email" in data
        assert "display_name" in data
        assert "is_admin" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated_returns_401(self, client: AsyncClient):
        """Get current user without auth returns 401."""
        response = await client.get("/auth/me")
        assert response.status_code == 401


class TestProfileContract:
    """Contract tests for PUT /profile."""

    @pytest_asyncio.fixture
    async def logged_in_client(self, client: AsyncClient):
        """Create a logged-in client."""
        await client.post(
            "/auth/register",
            json={
                "email": "profile@example.com",
                "password": "SecurePass123",
                "display_name": "ProfileUser",
            },
        )
        return client

    @pytest.mark.asyncio
    async def test_update_profile_returns_200(self, logged_in_client: AsyncClient):
        """Update profile returns 200."""
        response = await logged_in_client.put(
            "/profile",
            json={"display_name": "NewDisplayName"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_profile_response_structure(self, logged_in_client: AsyncClient):
        """Update profile response has correct structure."""
        response = await logged_in_client.put(
            "/profile",
            json={"display_name": "UpdatedName"},
        )
        data = response.json()

        assert "id" in data
        assert "email" in data
        assert "display_name" in data
        assert data["display_name"] == "UpdatedName"

    @pytest.mark.asyncio
    async def test_update_profile_unauthenticated_returns_401(self, client: AsyncClient):
        """Update profile without auth returns 401."""
        response = await client.put(
            "/profile",
            json={"display_name": "NewName"},
        )
        assert response.status_code == 401
