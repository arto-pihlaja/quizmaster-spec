"""QuizAttempt model for quiz taking."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from ..db import Base


class QuizAttempt(Base):
    """Represents a single attempt by a user to complete a quiz."""

    __tablename__ = "quiz_attempts"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False)  # FK to users when 002 is implemented
    quiz_id = Column(String, ForeignKey("quizzes.id", ondelete="SET NULL"), nullable=True)
    quiz_title_snapshot = Column(String(200), nullable=False)
    total_points_possible = Column(Integer, nullable=False)
    total_score = Column(Integer, nullable=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="in_progress")

    __table_args__ = (
        CheckConstraint("status IN ('in_progress', 'submitted')", name="check_status"),
        CheckConstraint("total_points_possible > 0", name="check_points_positive"),
        CheckConstraint("total_score IS NULL OR total_score >= 0", name="check_score_non_negative"),
    )

    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    answers = relationship(
        "AttemptAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
        order_by="AttemptAnswer.question_order",
    )

    def __repr__(self):
        return f"<QuizAttempt id={self.id} user={self.user_id} status={self.status}>"
