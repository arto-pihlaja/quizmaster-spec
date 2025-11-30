"""Quiz SQLAlchemy model."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..db import Base


class Quiz(Base):
    """Quiz entity representing a quiz created by a user."""

    __tablename__ = "quizzes"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(200), nullable=False)
    owner_id = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    questions = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan",
        order_by="Question.display_order",
    )
    attempts = relationship(
        "QuizAttempt",
        back_populates="quiz",
    )

    def __repr__(self) -> str:
        return f"<Quiz id={self.id} title={self.title!r}>"
