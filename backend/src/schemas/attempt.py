"""Pydantic schemas for quiz attempt API requests and responses."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# Request Schemas

class AnswerSubmission(BaseModel):
    """Schema for submitting an answer to a question."""

    question_id: UUID
    selected_answer_id: UUID


class SubmitRequest(BaseModel):
    """Schema for submitting quiz answers."""

    answers: List[AnswerSubmission] = Field(min_length=1)


# Response Schemas - Quiz Taking View (NO correct answers!)

class QuizTakingAnswer(BaseModel):
    """Answer option shown during quiz taking - NO is_correct field."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    # NOTE: is_correct intentionally omitted to prevent cheating


class QuizTakingQuestion(BaseModel):
    """Question shown during quiz taking."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order: int
    text: str
    answers: List[QuizTakingAnswer]


class QuizTakingView(BaseModel):
    """View of a quiz during taking - questions without correct answers."""

    model_config = ConfigDict(from_attributes=True)

    attempt_id: UUID
    quiz_title: str
    questions: List[QuizTakingQuestion]
    total_questions: int


# Response Schemas - Results (with correct answers)

class AttemptResultAnswer(BaseModel):
    """Answer result with correctness feedback."""

    model_config = ConfigDict(from_attributes=True)

    question_order: int
    question_text: str
    question_points: int
    selected_answer: Optional[str]
    correct_answer: str
    is_correct: bool
    points_earned: int


class AttemptResult(BaseModel):
    """Complete results of a submitted quiz attempt."""

    model_config = ConfigDict(from_attributes=True)

    attempt_id: UUID
    quiz_title: str
    total_score: int
    total_points_possible: int
    percentage: float
    submitted_at: datetime
    is_new_best: bool = False
    answers: List[AttemptResultAnswer]


# Response Schemas - Quiz Browser

class QuizBrowserItem(BaseModel):
    """Quiz item in the browser list."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    question_count: int
    user_attempts: int
    user_best_score: Optional[int] = None
    user_best_percentage: Optional[float] = None


class QuizBrowserResponse(BaseModel):
    """Response for quiz browser endpoint."""

    quizzes: List[QuizBrowserItem]


# Response Schemas - History

class AttemptHistoryItem(BaseModel):
    """Single attempt in history list."""

    model_config = ConfigDict(from_attributes=True)

    attempt_id: UUID
    quiz_title: str
    total_score: int
    total_points_possible: int
    percentage: float
    submitted_at: datetime
    is_best: bool


class AttemptHistoryResponse(BaseModel):
    """Response for quiz-specific attempt history."""

    quiz_id: UUID
    quiz_title: str
    attempts: List[AttemptHistoryItem]


class MyAttemptsResponse(BaseModel):
    """Response for user's all attempts across quizzes."""

    attempts: List[AttemptHistoryItem]
    total: int
    limit: int
    offset: int
