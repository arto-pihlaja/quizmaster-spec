"""Integration tests for scoreboard feature."""

import pytest
from httpx import AsyncClient

from src.models.user_score import UserScore
from src.models.quiz import Quiz
from src.models.attempt import QuizAttempt


class TestScoreboardDisplayFlow:
    """Integration tests for scoreboard display (US1)."""

    @pytest.mark.asyncio
    async def test_scoreboard_displays_users_in_order(self, client: AsyncClient, test_db):
        """Scoreboard displays users ranked by score."""
        # Create test users with different scores
        test_db.add_all([
            UserScore(user_id="alice", display_name="Alice", total_score=150, quizzes_completed=3),
            UserScore(user_id="bob", display_name="Bob", total_score=300, quizzes_completed=5),
            UserScore(user_id="charlie", display_name="Charlie", total_score=100, quizzes_completed=2),
        ])
        await test_db.commit()

        # Get scoreboard
        response = await client.get("/api/scoreboard")
        assert response.status_code == 200

        data = response.json()
        entries = data["entries"]

        # Verify order: Bob (300) > Alice (150) > Charlie (100)
        assert len(entries) == 3
        assert entries[0]["display_name"] == "Bob"
        assert entries[0]["rank"] == 1
        assert entries[1]["display_name"] == "Alice"
        assert entries[1]["rank"] == 2
        assert entries[2]["display_name"] == "Charlie"
        assert entries[2]["rank"] == 3


class TestScoreDetailsAccuracy:
    """Integration tests for score details (US2)."""

    @pytest.mark.asyncio
    async def test_score_details_match_data(self, client: AsyncClient, test_db):
        """Displayed details match stored data."""
        test_db.add(UserScore(
            user_id="alice",
            display_name="Alice",
            total_score=250,
            quizzes_completed=7
        ))
        await test_db.commit()

        response = await client.get("/api/scoreboard")
        entry = response.json()["entries"][0]

        assert entry["display_name"] == "Alice"
        assert entry["total_score"] == 250
        assert entry["quizzes_completed"] == 7
        assert entry["rank"] == 1


class TestUserHighlighting:
    """Integration tests for user highlighting (US3)."""

    @pytest.mark.asyncio
    async def test_current_user_id_included_when_authenticated(self, client: AsyncClient, test_db):
        """Response includes current_user_id when authenticated."""
        test_db.add(UserScore(user_id="alice", display_name="Alice", total_score=100))
        await test_db.commit()

        response = await client.get(
            "/api/scoreboard",
            cookies={"user_id": "alice"}
        )
        data = response.json()

        assert data["current_user_id"] == "alice"

    @pytest.mark.asyncio
    async def test_current_user_id_none_when_not_authenticated(self, client: AsyncClient, test_db):
        """Response has null current_user_id when not authenticated."""
        test_db.add(UserScore(user_id="alice", display_name="Alice", total_score=100))
        await test_db.commit()

        response = await client.get("/api/scoreboard")
        data = response.json()

        assert data["current_user_id"] is None


class TestScoreUpdateAfterQuiz:
    """Integration tests for score updates (US4)."""

    @pytest.mark.asyncio
    async def test_scoreboard_reflects_score_changes(self, client: AsyncClient, test_db):
        """Scoreboard reflects updated scores after refresh."""
        # Initial score
        test_db.add(UserScore(user_id="alice", display_name="Alice", total_score=100))
        await test_db.commit()

        # Get initial scoreboard
        response1 = await client.get("/api/scoreboard")
        assert response1.json()["entries"][0]["total_score"] == 100

        # Update score (simulating quiz completion)
        user_score = await test_db.get(UserScore, "alice")
        user_score.total_score = 200
        await test_db.commit()

        # Refresh scoreboard
        response2 = await client.get("/api/scoreboard")
        assert response2.json()["entries"][0]["total_score"] == 200


class TestEmptyScoreboard:
    """Integration tests for empty scoreboard state."""

    @pytest.mark.asyncio
    async def test_empty_scoreboard_returns_valid_response(self, client: AsyncClient, test_db):
        """Empty scoreboard returns valid response structure."""
        response = await client.get("/api/scoreboard")
        assert response.status_code == 200

        data = response.json()
        assert data["entries"] == []
        assert data["pagination"]["total_entries"] == 0


class TestScoreboardPagination:
    """Integration tests for scoreboard pagination."""

    @pytest.mark.asyncio
    async def test_pagination_navigates_correctly(self, client: AsyncClient, test_db):
        """Pagination allows navigating through all users."""
        # Add 75 users
        for i in range(75):
            test_db.add(UserScore(
                user_id=f"user{i:03d}",
                display_name=f"User {i:03d}",
                total_score=1000 - i
            ))
        await test_db.commit()

        # Page 1
        resp1 = await client.get("/api/scoreboard?page=1&page_size=25")
        data1 = resp1.json()
        assert len(data1["entries"]) == 25
        assert data1["pagination"]["has_next"] is True
        assert data1["pagination"]["has_prev"] is False

        # Page 2
        resp2 = await client.get("/api/scoreboard?page=2&page_size=25")
        data2 = resp2.json()
        assert len(data2["entries"]) == 25
        assert data2["pagination"]["has_next"] is True
        assert data2["pagination"]["has_prev"] is True

        # Page 3 (last)
        resp3 = await client.get("/api/scoreboard?page=3&page_size=25")
        data3 = resp3.json()
        assert len(data3["entries"]) == 25
        assert data3["pagination"]["has_next"] is False
        assert data3["pagination"]["has_prev"] is True

        # Entries should not overlap
        ids1 = {e["user_id"] for e in data1["entries"]}
        ids2 = {e["user_id"] for e in data2["entries"]}
        ids3 = {e["user_id"] for e in data3["entries"]}
        assert ids1.isdisjoint(ids2)
        assert ids2.isdisjoint(ids3)
