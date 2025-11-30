"""Unit tests for ScoreboardService."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_score import UserScore
from src.services.scoreboard import ScoreboardService


class TestGetScoreboard:
    """Unit tests for ScoreboardService.get_scoreboard()."""

    @pytest.mark.asyncio
    async def test_get_scoreboard_empty(self, test_db: AsyncSession):
        """Returns empty entries when no users."""
        service = ScoreboardService(test_db)
        result = await service.get_scoreboard()

        assert result.entries == []
        assert result.pagination.total_entries == 0
        assert result.pagination.total_pages == 1

    @pytest.mark.asyncio
    async def test_get_scoreboard_returns_entries(self, test_db: AsyncSession):
        """Returns entries ordered by score descending."""
        test_db.add_all([
            UserScore(user_id="u1", display_name="Alice", total_score=100),
            UserScore(user_id="u2", display_name="Bob", total_score=200),
            UserScore(user_id="u3", display_name="Charlie", total_score=150),
        ])
        await test_db.commit()

        service = ScoreboardService(test_db)
        result = await service.get_scoreboard()

        assert len(result.entries) == 3
        assert result.entries[0].display_name == "Bob"
        assert result.entries[0].total_score == 200
        assert result.entries[0].rank == 1
        assert result.entries[1].display_name == "Charlie"
        assert result.entries[1].rank == 2
        assert result.entries[2].display_name == "Alice"
        assert result.entries[2].rank == 3

    @pytest.mark.asyncio
    async def test_get_scoreboard_pagination(self, test_db: AsyncSession):
        """Pagination works correctly."""
        for i in range(25):
            test_db.add(UserScore(user_id=f"u{i}", display_name=f"User{i}", total_score=100-i))
        await test_db.commit()

        service = ScoreboardService(test_db)
        result = await service.get_scoreboard(page=2, page_size=10)

        assert len(result.entries) == 10
        assert result.pagination.page == 2
        assert result.pagination.total_entries == 25
        assert result.pagination.total_pages == 3
        assert result.pagination.has_prev is True
        assert result.pagination.has_next is True


class TestCompetitionRanking:
    """Unit tests for competition ranking (tied scores) (US2)."""

    @pytest.mark.asyncio
    async def test_tied_scores_same_rank(self, test_db: AsyncSession):
        """Tied scores get the same rank (competition ranking).

        RANK() with ORDER BY total_score DESC, display_name ASC
        gives same rank for truly identical sort keys.
        """
        # Create users with SAME display_name prefix to test true ties
        test_db.add_all([
            UserScore(user_id="u1", display_name="Alice", total_score=100),
            UserScore(user_id="u2", display_name="Alice", total_score=100),  # Same name = true tie
            UserScore(user_id="u3", display_name="Charlie", total_score=50),
        ])
        await test_db.commit()

        service = ScoreboardService(test_db)
        result = await service.get_scoreboard()

        # Both Alices have same score and same name
        alices = [e for e in result.entries if e.display_name == "Alice"]
        charlie = next(e for e in result.entries if e.display_name == "Charlie")

        # Both Alices should have rank 1 (truly tied on both sort keys)
        assert len(alices) == 2
        assert all(a.rank == 1 for a in alices)
        # Charlie should have rank 3 (skips 2 because two people share 1st)
        assert charlie.rank == 3

    @pytest.mark.asyncio
    async def test_tied_scores_secondary_sort_by_name(self, test_db: AsyncSession):
        """Tied scores are sorted alphabetically by display name."""
        test_db.add_all([
            UserScore(user_id="u1", display_name="Zoe", total_score=100),
            UserScore(user_id="u2", display_name="Alice", total_score=100),
        ])
        await test_db.commit()

        service = ScoreboardService(test_db)
        result = await service.get_scoreboard()

        # Alice should appear before Zoe (alphabetical)
        assert result.entries[0].display_name == "Alice"
        assert result.entries[1].display_name == "Zoe"


class TestGetUserRank:
    """Unit tests for ScoreboardService.get_user_rank() (US3)."""

    @pytest.mark.asyncio
    async def test_get_user_rank_returns_rank(self, test_db: AsyncSession):
        """Returns correct rank for user."""
        test_db.add_all([
            UserScore(user_id="u1", display_name="Alice", total_score=100),
            UserScore(user_id="u2", display_name="Bob", total_score=200),
            UserScore(user_id="u3", display_name="Charlie", total_score=150),
        ])
        await test_db.commit()

        service = ScoreboardService(test_db)

        # Alice is 3rd
        result = await service.get_user_rank("u1")
        assert result is not None
        assert result.rank == 3
        assert result.total_score == 100

        # Bob is 1st
        result = await service.get_user_rank("u2")
        assert result.rank == 1

    @pytest.mark.asyncio
    async def test_get_user_rank_calculates_page(self, test_db: AsyncSession):
        """Calculates correct page for user's rank."""
        for i in range(100):
            test_db.add(UserScore(user_id=f"u{i}", display_name=f"User{i:03d}", total_score=1000-i))
        await test_db.commit()

        service = ScoreboardService(test_db)

        # User with rank 75 should be on page 2 (with page_size=50)
        result = await service.get_user_rank("u74", page_size=50)  # 0-indexed, so u74 is 75th
        assert result is not None
        assert result.rank == 75
        assert result.page == 2

    @pytest.mark.asyncio
    async def test_get_user_rank_not_found(self, test_db: AsyncSession):
        """Returns None for non-existent user."""
        service = ScoreboardService(test_db)
        result = await service.get_user_rank("nonexistent")
        assert result is None


class TestGetStats:
    """Unit tests for ScoreboardService.get_stats() (US2)."""

    @pytest.mark.asyncio
    async def test_get_stats_empty(self, test_db: AsyncSession):
        """Returns zeros for empty scoreboard."""
        service = ScoreboardService(test_db)
        result = await service.get_stats()

        assert result.total_users == 0
        assert result.total_quizzes_taken == 0
        assert result.highest_score == 0
        assert result.average_score == 0

    @pytest.mark.asyncio
    async def test_get_stats_with_data(self, test_db: AsyncSession):
        """Returns correct aggregate stats."""
        test_db.add_all([
            UserScore(user_id="u1", display_name="Alice", total_score=100, quizzes_completed=5),
            UserScore(user_id="u2", display_name="Bob", total_score=200, quizzes_completed=10),
            UserScore(user_id="u3", display_name="Charlie", total_score=150, quizzes_completed=7),
        ])
        await test_db.commit()

        service = ScoreboardService(test_db)
        result = await service.get_stats()

        assert result.total_users == 3
        assert result.total_quizzes_taken == 22
        assert result.highest_score == 200
        assert result.average_score == 150.0  # (100+200+150)/3


class TestUpdateUserScore:
    """Unit tests for ScoreboardService.update_user_score()."""

    @pytest.mark.asyncio
    async def test_update_creates_user_score(self, test_db: AsyncSession):
        """Creates new UserScore if not exists."""
        service = ScoreboardService(test_db)
        result = await service.update_user_score("user1", "Alice")
        await test_db.commit()

        assert result.user_id == "user1"
        assert result.display_name == "Alice"

    @pytest.mark.asyncio
    async def test_update_existing_user_score(self, test_db: AsyncSession):
        """Updates existing UserScore."""
        test_db.add(UserScore(user_id="user1", display_name="Alice", total_score=50))
        await test_db.commit()

        service = ScoreboardService(test_db)
        result = await service.update_user_score("user1", "Alice Updated")
        await test_db.commit()

        # Should still have same user_id but updated
        assert result.user_id == "user1"
