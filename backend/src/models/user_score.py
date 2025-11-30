"""UserScore model for scoreboard feature."""

from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, CheckConstraint, Index

from ..db import Base


class UserScore(Base):
    """Pre-aggregated score data for efficient scoreboard queries.

    One row per user (1:1 with users).
    Updated when user completes a quiz.
    total_score = sum of best attempt per quiz (not all attempts).
    """

    __tablename__ = "user_scores"

    user_id = Column(String, primary_key=True)
    display_name = Column(String(100), nullable=False, default="Anonymous")
    total_score = Column(Integer, nullable=False, default=0)
    quizzes_completed = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("total_score >= 0", name="check_total_score_non_negative"),
        CheckConstraint("quizzes_completed >= 0", name="check_quizzes_completed_non_negative"),
        Index("idx_user_scores_ranking", total_score.desc(), display_name.asc()),
    )

    def __repr__(self):
        return f"<UserScore user_id={self.user_id} score={self.total_score}>"
