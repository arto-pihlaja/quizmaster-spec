"""ScoreboardService for scoreboard feature."""

import logging
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user_score import UserScore
from ..models.attempt import QuizAttempt
from ..schemas.scoreboard import (
    ScoreboardEntry,
    Pagination,
    ScoreboardResponse,
    MyRankResponse,
    ScoreboardStats,
)

logger = logging.getLogger(__name__)


class ScoreboardService:
    """Service for scoreboard operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_scoreboard(
        self,
        page: int = 1,
        page_size: int = 50,
        current_user_id: Optional[str] = None,
    ) -> ScoreboardResponse:
        """Get paginated scoreboard with competition ranking.

        Uses RANK() window function for competition ranking (1, 2, 2, 4).
        """
        logger.info(f"Getting scoreboard page={page} page_size={page_size}")

        # Get total count
        total_entries = await self.get_total_count()
        total_pages = max(1, (total_entries + page_size - 1) // page_size)

        # Validate page
        if page < 1:
            page = 1
        if page > total_pages and total_pages > 0:
            page = total_pages

        offset = (page - 1) * page_size

        # Query with RANK() window function
        # SQLite supports window functions since 3.25+
        ranked_query = text("""
            SELECT
                user_id,
                display_name,
                total_score,
                quizzes_completed,
                RANK() OVER (ORDER BY total_score DESC, display_name ASC) as rank
            FROM user_scores
            ORDER BY rank
            LIMIT :limit OFFSET :offset
        """)

        result = await self.db.execute(
            ranked_query,
            {"limit": page_size, "offset": offset}
        )
        rows = result.fetchall()

        entries = [
            ScoreboardEntry(
                rank=row.rank,
                user_id=row.user_id,
                display_name=row.display_name,
                total_score=row.total_score,
                quizzes_completed=row.quizzes_completed,
            )
            for row in rows
        ]

        pagination = Pagination(
            page=page,
            page_size=page_size,
            total_entries=total_entries,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

        return ScoreboardResponse(
            entries=entries,
            pagination=pagination,
            current_user_id=current_user_id,
        )

    async def get_total_count(self) -> int:
        """Get total number of users on the scoreboard."""
        result = await self.db.execute(
            select(func.count()).select_from(UserScore)
        )
        return result.scalar() or 0

    async def get_user_rank(self, user_id: str, page_size: int = 50) -> Optional[MyRankResponse]:
        """Get the rank and page for a specific user.

        Returns None if user has no score record.
        """
        logger.info(f"Getting rank for user_id={user_id}")

        # First check if user exists
        user_result = await self.db.execute(
            select(UserScore).where(UserScore.user_id == user_id)
        )
        user_score = user_result.scalar_one_or_none()

        if not user_score:
            return None

        # Get user's rank using RANK() window function
        rank_query = text("""
            WITH ranked AS (
                SELECT
                    user_id,
                    total_score,
                    quizzes_completed,
                    RANK() OVER (ORDER BY total_score DESC, display_name ASC) as rank
                FROM user_scores
            )
            SELECT rank, total_score, quizzes_completed
            FROM ranked
            WHERE user_id = :user_id
        """)

        result = await self.db.execute(rank_query, {"user_id": user_id})
        row = result.fetchone()

        if not row:
            return None

        # Calculate which page the user is on
        page = ((row.rank - 1) // page_size) + 1

        return MyRankResponse(
            user_id=user_id,
            rank=row.rank,
            page=page,
            total_score=row.total_score,
            quizzes_completed=row.quizzes_completed,
        )

    async def get_stats(self) -> ScoreboardStats:
        """Get aggregate statistics for the scoreboard."""
        logger.info("Getting scoreboard stats")

        # Get aggregated stats
        stats_query = select(
            func.count(UserScore.user_id).label("total_users"),
            func.sum(UserScore.quizzes_completed).label("total_quizzes"),
            func.max(UserScore.total_score).label("highest_score"),
            func.avg(UserScore.total_score).label("average_score"),
        )

        result = await self.db.execute(stats_query)
        row = result.fetchone()

        return ScoreboardStats(
            total_users=row.total_users or 0,
            total_quizzes_taken=row.total_quizzes or 0,
            highest_score=row.highest_score or 0,
            average_score=float(row.average_score or 0),
        )

    async def update_user_score(self, user_id: str, display_name: str = "Anonymous") -> UserScore:
        """Update a user's aggregated score after quiz completion.

        Calculates total score from best attempt per quiz.
        """
        logger.info(f"Updating score for user_id={user_id}")

        # Get best score per quiz for this user
        best_scores_query = text("""
            SELECT
                quiz_id,
                MAX(total_score) as best_score
            FROM quiz_attempts
            WHERE user_id = :user_id
              AND status = 'submitted'
              AND quiz_id IS NOT NULL
            GROUP BY quiz_id
        """)

        result = await self.db.execute(best_scores_query, {"user_id": user_id})
        rows = result.fetchall()

        total_score = sum(row.best_score or 0 for row in rows)
        quizzes_completed = len(rows)

        # Upsert user score
        existing = await self.db.execute(
            select(UserScore).where(UserScore.user_id == user_id)
        )
        user_score = existing.scalar_one_or_none()

        if user_score:
            user_score.total_score = total_score
            user_score.quizzes_completed = quizzes_completed
            user_score.last_updated = datetime.utcnow()
            if display_name and display_name != "Anonymous":
                user_score.display_name = display_name
        else:
            user_score = UserScore(
                user_id=user_id,
                display_name=display_name,
                total_score=total_score,
                quizzes_completed=quizzes_completed,
                last_updated=datetime.utcnow(),
            )
            self.db.add(user_score)

        await self.db.flush()
        return user_score

    async def ensure_user_exists(self, user_id: str, display_name: str = "Anonymous") -> UserScore:
        """Ensure a user exists in the user_scores table.

        Creates with zero score if not exists.
        """
        existing = await self.db.execute(
            select(UserScore).where(UserScore.user_id == user_id)
        )
        user_score = existing.scalar_one_or_none()

        if not user_score:
            user_score = UserScore(
                user_id=user_id,
                display_name=display_name,
                total_score=0,
                quizzes_completed=0,
                last_updated=datetime.utcnow(),
            )
            self.db.add(user_score)
            await self.db.flush()

        return user_score
