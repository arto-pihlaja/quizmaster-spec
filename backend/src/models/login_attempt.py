"""LoginAttempt SQLAlchemy model."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, String

from ..db import Base


class LoginAttempt(Base):
    """LoginAttempt model for tracking failed login attempts and account lockout."""

    __tablename__ = "login_attempts"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    attempt_count = Column(Integer, nullable=False, default=0)
    last_attempt_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    locked_until = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<LoginAttempt(email={self.email}, attempt_count={self.attempt_count}, locked_until={self.locked_until})>"

    @property
    def is_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
