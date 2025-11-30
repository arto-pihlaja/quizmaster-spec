"""Contract tests for Scoreboard API endpoints."""

import pytest
from httpx import AsyncClient

from src.models.user_score import UserScore


class TestGetScoreboardContract:
    """Contract tests for GET /api/scoreboard."""

    @pytest.mark.asyncio
    async def test_get_scoreboard_returns_200(self, client: AsyncClient, test_db):
        """GET /api/scoreboard returns 200 OK."""
        response = await client.get("/api/scoreboard")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_scoreboard_response_structure(self, client: AsyncClient, test_db):
        """Response has correct structure with entries and pagination."""
        response = await client.get("/api/scoreboard")
        data = response.json()

        assert "entries" in data
        assert "pagination" in data
        assert isinstance(data["entries"], list)

        # Pagination structure
        pagination = data["pagination"]
        assert "page" in pagination
        assert "page_size" in pagination
        assert "total_entries" in pagination
        assert "total_pages" in pagination
        assert "has_next" in pagination
        assert "has_prev" in pagination

    @pytest.mark.asyncio
    async def test_get_scoreboard_with_data(self, client: AsyncClient, test_db):
        """Scoreboard returns entries when data exists."""
        # Add test users
        user1 = UserScore(user_id="user1", display_name="Alice", total_score=100, quizzes_completed=5)
        user2 = UserScore(user_id="user2", display_name="Bob", total_score=200, quizzes_completed=10)
        test_db.add_all([user1, user2])
        await test_db.commit()

        response = await client.get("/api/scoreboard")
        data = response.json()

        assert len(data["entries"]) == 2
        # Bob should be first (higher score)
        assert data["entries"][0]["display_name"] == "Bob"
        assert data["entries"][0]["rank"] == 1
        assert data["entries"][1]["display_name"] == "Alice"
        assert data["entries"][1]["rank"] == 2

    @pytest.mark.asyncio
    async def test_get_scoreboard_pagination_params(self, client: AsyncClient, test_db):
        """Scoreboard respects page and page_size params."""
        # Add 60 users
        for i in range(60):
            user = UserScore(user_id=f"user{i}", display_name=f"User{i:02d}", total_score=1000-i)
            test_db.add(user)
        await test_db.commit()

        # Request page 2 with 10 items
        response = await client.get("/api/scoreboard?page=2&page_size=10")
        data = response.json()

        assert len(data["entries"]) == 10
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["page_size"] == 10
        assert data["pagination"]["total_entries"] == 60
        assert data["pagination"]["total_pages"] == 6
        assert data["pagination"]["has_prev"] is True
        assert data["pagination"]["has_next"] is True


class TestGetScoreboardPageContract:
    """Contract tests for GET /scoreboard HTML page."""

    @pytest.mark.asyncio
    async def test_scoreboard_page_returns_200(self, client: AsyncClient, test_db):
        """GET /scoreboard returns 200 OK with HTML."""
        response = await client.get("/scoreboard")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_scoreboard_page_contains_title(self, client: AsyncClient, test_db):
        """Scoreboard page contains 'Scoreboard' in content."""
        response = await client.get("/scoreboard")
        assert "Scoreboard" in response.text


class TestScoreboardEntryStructure:
    """Contract tests for ScoreboardEntry structure (US2)."""

    @pytest.mark.asyncio
    async def test_entry_has_required_fields(self, client: AsyncClient, test_db):
        """Each entry has rank, user_id, display_name, total_score."""
        user = UserScore(user_id="user1", display_name="Alice", total_score=100)
        test_db.add(user)
        await test_db.commit()

        response = await client.get("/api/scoreboard")
        data = response.json()
        entry = data["entries"][0]

        assert "rank" in entry
        assert "user_id" in entry
        assert "display_name" in entry
        assert "total_score" in entry
        assert "quizzes_completed" in entry


class TestGetScoreboardStatsContract:
    """Contract tests for GET /api/scoreboard/stats (US2)."""

    @pytest.mark.asyncio
    async def test_stats_returns_200(self, client: AsyncClient, test_db):
        """GET /api/scoreboard/stats returns 200 OK."""
        response = await client.get("/api/scoreboard/stats")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_stats_response_structure(self, client: AsyncClient, test_db):
        """Stats response has correct structure."""
        response = await client.get("/api/scoreboard/stats")
        data = response.json()

        assert "total_users" in data
        assert "total_quizzes_taken" in data
        assert "highest_score" in data
        assert "average_score" in data

    @pytest.mark.asyncio
    async def test_stats_with_data(self, client: AsyncClient, test_db):
        """Stats are calculated correctly from data."""
        user1 = UserScore(user_id="user1", display_name="Alice", total_score=100, quizzes_completed=5)
        user2 = UserScore(user_id="user2", display_name="Bob", total_score=200, quizzes_completed=10)
        test_db.add_all([user1, user2])
        await test_db.commit()

        response = await client.get("/api/scoreboard/stats")
        data = response.json()

        assert data["total_users"] == 2
        assert data["total_quizzes_taken"] == 15
        assert data["highest_score"] == 200
        assert data["average_score"] == 150.0


class TestGetMyRankContract:
    """Contract tests for GET /api/scoreboard/my-rank (US3)."""

    @pytest.mark.asyncio
    async def test_my_rank_requires_auth(self, client: AsyncClient, test_db):
        """GET /api/scoreboard/my-rank returns 401 without auth."""
        response = await client.get("/api/scoreboard/my-rank")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_my_rank_returns_200_when_authenticated(self, client: AsyncClient, test_db):
        """GET /api/scoreboard/my-rank returns 200 with auth."""
        user = UserScore(user_id="user1", display_name="Alice", total_score=100)
        test_db.add(user)
        await test_db.commit()

        response = await client.get(
            "/api/scoreboard/my-rank",
            cookies={"user_id": "user1"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_my_rank_response_structure(self, client: AsyncClient, test_db):
        """My rank response has correct structure."""
        user = UserScore(user_id="user1", display_name="Alice", total_score=100)
        test_db.add(user)
        await test_db.commit()

        response = await client.get(
            "/api/scoreboard/my-rank",
            cookies={"user_id": "user1"}
        )
        data = response.json()

        assert "user_id" in data
        assert "rank" in data
        assert "page" in data
        assert "total_score" in data
        assert "quizzes_completed" in data

    @pytest.mark.asyncio
    async def test_my_rank_returns_404_no_score(self, client: AsyncClient, test_db):
        """GET /api/scoreboard/my-rank returns 404 if user has no score."""
        response = await client.get(
            "/api/scoreboard/my-rank",
            cookies={"user_id": "nonexistent"}
        )
        assert response.status_code == 404


class TestRefreshResponseStructure:
    """Contract tests for refresh response (US4)."""

    @pytest.mark.asyncio
    async def test_refresh_returns_same_structure(self, client: AsyncClient, test_db):
        """Refresh (same endpoint) returns consistent structure."""
        # First request
        response1 = await client.get("/api/scoreboard")
        data1 = response1.json()

        # Add user
        user = UserScore(user_id="user1", display_name="Alice", total_score=100)
        test_db.add(user)
        await test_db.commit()

        # Second request (simulating refresh)
        response2 = await client.get("/api/scoreboard")
        data2 = response2.json()

        # Structure should be consistent
        assert set(data1.keys()) == set(data2.keys())
        assert set(data1["pagination"].keys()) == set(data2["pagination"].keys())
