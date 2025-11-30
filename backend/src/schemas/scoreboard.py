"""Pydantic schemas for scoreboard feature."""

from typing import Optional
from pydantic import BaseModel, Field


class ScoreboardEntry(BaseModel):
    """A single entry on the scoreboard."""

    rank: int = Field(..., ge=1, description="Competition ranking position")
    user_id: str = Field(..., description="User's unique identifier")
    display_name: str = Field(..., description="User's display name")
    total_score: int = Field(..., ge=0, description="Total points earned across all quizzes")
    quizzes_completed: int = Field(0, ge=0, description="Number of unique quizzes completed")

    model_config = {"from_attributes": True}


class Pagination(BaseModel):
    """Pagination metadata for scoreboard responses."""

    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=10, le=100, description="Entries per page")
    total_entries: int = Field(..., ge=0, description="Total number of users on scoreboard")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class ScoreboardResponse(BaseModel):
    """Response containing scoreboard data with pagination."""

    entries: list[ScoreboardEntry] = Field(..., description="List of scoreboard entries for current page")
    pagination: Pagination = Field(..., description="Pagination metadata")
    current_user_id: Optional[str] = Field(None, description="ID of logged-in user for highlighting")


class MyRankResponse(BaseModel):
    """Response containing the current user's rank information."""

    user_id: str = Field(..., description="User's unique identifier")
    rank: int = Field(..., ge=1, description="User's current rank")
    page: int = Field(..., ge=1, description="Page number where user appears")
    total_score: int = Field(..., ge=0, description="User's total score")
    quizzes_completed: int = Field(0, ge=0, description="User's quiz count")


class ScoreboardStats(BaseModel):
    """Aggregate statistics about the scoreboard."""

    total_users: int = Field(..., ge=0, description="Total users on scoreboard")
    total_quizzes_taken: int = Field(..., ge=0, description="Sum of all quizzes completed")
    highest_score: int = Field(..., ge=0, description="Top score on the leaderboard")
    average_score: float = Field(..., ge=0, description="Average score across all users")
