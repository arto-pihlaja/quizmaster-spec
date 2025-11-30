"""Question SQLAlchemy model."""

from uuid import uuid4

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..db import Base


class Question(Base):
    """Question entity representing a single question within a quiz."""

    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    quiz_id = Column(String, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(1000), nullable=False)
    display_order = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False, default=1)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="Answer.display_order",
    )

    def __repr__(self) -> str:
        return f"<Question id={self.id} text={self.text[:50]!r}...>"
