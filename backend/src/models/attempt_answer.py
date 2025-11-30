"""AttemptAnswer model for storing user answers in quiz attempts."""

from uuid import uuid4

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from ..db import Base


class AttemptAnswer(Base):
    """Stores the user's answer for each question in an attempt."""

    __tablename__ = "attempt_answers"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    attempt_id = Column(
        String,
        ForeignKey("quiz_attempts.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id = Column(
        String,
        ForeignKey("questions.id", ondelete="SET NULL"),
        nullable=True,
    )
    question_order = Column(Integer, nullable=False)
    question_text_snapshot = Column(String(1000), nullable=False)
    question_points = Column(Integer, nullable=False)
    selected_answer_id = Column(String, nullable=True)
    selected_answer_text = Column(String(500), nullable=True)
    correct_answer_text = Column(String(500), nullable=False)
    is_correct = Column(Boolean, nullable=True)
    points_earned = Column(Integer, nullable=True)

    __table_args__ = (
        CheckConstraint("question_order >= 1", name="check_order_positive"),
        CheckConstraint("question_points >= 1", name="check_points_positive"),
        CheckConstraint("points_earned IS NULL OR points_earned >= 0", name="check_earned_non_negative"),
    )

    # Relationships
    attempt = relationship("QuizAttempt", back_populates="answers")
    question = relationship("Question")

    def __repr__(self):
        return f"<AttemptAnswer id={self.id} question_order={self.question_order}>"
