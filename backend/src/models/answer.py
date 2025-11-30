"""Answer SQLAlchemy model."""

from uuid import uuid4

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ..db import Base


class Answer(Base):
    """Answer entity representing a possible answer option for a question."""

    __tablename__ = "answers"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    question_id = Column(String, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(500), nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    display_order = Column(Integer, nullable=False)

    # Relationships
    question = relationship("Question", back_populates="answers")

    def __repr__(self) -> str:
        return f"<Answer id={self.id} text={self.text[:30]!r}... correct={self.is_correct}>"
