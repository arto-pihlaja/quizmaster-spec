"""Pydantic schemas for quiz API requests and responses."""

from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# Request Schemas

class AnswerCreate(BaseModel):
    """Schema for creating an answer option."""

    text: str = Field(min_length=1, max_length=500, description="Answer text")
    is_correct: bool = Field(default=False, description="Whether this is the correct answer")

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Answer text is required")
        return v.strip()


class QuestionCreate(BaseModel):
    """Schema for creating a question."""

    text: str = Field(min_length=1, max_length=1000, description="Question text")
    answers: List[AnswerCreate] = Field(
        min_length=2, max_length=6, description="Answer options (2-6 required)"
    )
    points: int = Field(default=1, ge=1, le=100, description="Points for correct answer")

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Question text is required")
        return v.strip()

    @field_validator("answers")
    @classmethod
    def exactly_one_correct(cls, v: List[AnswerCreate]) -> List[AnswerCreate]:
        correct_count = sum(1 for a in v if a.is_correct)
        if correct_count != 1:
            raise ValueError("Question must have exactly one correct answer")
        return v


class QuizCreate(BaseModel):
    """Schema for creating a quiz."""

    title: str = Field(min_length=1, max_length=200, description="Quiz title")
    questions: List[QuestionCreate] = Field(
        min_length=1, max_length=100, description="Quiz questions (1-100 required)"
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title is required")
        return v.strip()


# Response Schemas

class AnswerResponse(BaseModel):
    """Schema for answer in API response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    is_correct: bool


class QuestionResponse(BaseModel):
    """Schema for question in API response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    answers: List[AnswerResponse]
    display_order: int
    points: int


class QuizResponse(BaseModel):
    """Schema for full quiz in API response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    owner_id: UUID
    questions: List[QuestionResponse]
    created_at: datetime
    updated_at: datetime


class QuizListItem(BaseModel):
    """Schema for quiz in list view."""

    id: UUID
    title: str
    question_count: int
    created_at: datetime
    updated_at: datetime


class QuizListResponse(BaseModel):
    """Schema for quiz list API response."""

    quizzes: List[QuizListItem]
